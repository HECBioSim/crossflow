'''
Clients.py: thin wrapper over dask client
'''
import socket
import subprocess
import tempfile
import glob
from collections import Iterable
from dask.distributed import Client as DaskClient
from dask.distributed import LocalCluster
from .kernels import FunctionKernel, SubprocessKernel
from .filehandling import FileHandler, FileHandle
from . import config

def dask_client(scheduler_file=None, local=False, port=8786):
    """
    returns an instance of a dask.distributed client
    """
    if local:
#        if __name__ == '__main__':
            workdir = tempfile.mkdtemp()
            cluster = LocalCluster(local_directory=workdir)
            client = DaskClient(cluster)
#        else:
#            raise IOError('Error: local cluster must be started within the __main__ block of the script not from {}'.format(__name__))

    elif scheduler_file:
        client = DaskClient(scheduler_file=scheduler_file)
    else:
        ip_address = socket.gethostbyname(socket.gethostname())
        dask_scheduler = '{}:{}'.format(ip_address, port)
        try:
            client = DaskClient(dask_scheduler, timeout=5)
        except IOError:
            print('Error: cannot connect to dask scheduler at {}'.format(dask_scheduler))
            raise
    return client

class Client(object):
    '''Thin wrapper around Dask client so functions that return multiple
       values (tuples) generate tuples of futures rather than single futures.
    '''
    def __init__(self, **kwargs):
        self.client = dask_client(**kwargs)
        self.filehandler = FileHandler(config.stage_point)

    def close(self):
        """
        The close() method of the underlying dask client
        """
        return self.client.close()

    def upload(self, some_object):
        """
        Upload some data/object to the.workers

        args:
            fsome_object (any type): what to upload

        returns:
            dask.Future
        """
        try:
            some_object = self.filehandler.load(some_object)
        except:
            pass
        return self.client.scatter(some_object, broadcast=True)

    def unpack(self, kernel, future):
        """
        Unpacks the single future returned by kernel when run through
        a dask submit() or map() method, returning a tuple of futures.

        The outputs attribute of kernel lists how many values kernel
        should properly return.

        args:
            kernel (Kernel): the kernel that generated the future
            future (Future): the future returned by kernel

        returns:
            future or tuple of futures.
        """
        if len(kernel.outputs) == 1:
            return future
        outputs = []
        for i in range(len(kernel.outputs)):
            outputs.append(self.client.submit(lambda tup, j: tup[j], future, i))
        return tuple(outputs)

    def _filehandlify(self, args):
        """
        work through an argument list, converting paths to filehandles
        where possible.
        """
        if isinstance(args, list):
            newargs = []
            for a in args:
                if isinstance(a, list):
                    newa = []
                    for b in a:
                        if isinstance(b, Iterable):
                            if '?' in b or '*' in b:
                                blist = glob.glob(b)
                                blist.sort()
                                if len(blist) > 0:
                                    newb = []
                                    for c in blist:
                                        try:
                                            c = self.filehandler.load(c)
                                        except:
                                            pass
                                        newb.append(c)
                                else:
                                    try:
                                        newb = self.filehandler.load(b)
                                    except:
                                        newb = b
                            else:
                                try:
                                    newb = self.filehandler.load(b)
                                except:
                                    newb = b
                        else:
                            try:
                                newb = self.filehandler.load(b)
                            except:
                                newb = b

                        newa.append(newb)
                else:
                    if isinstance(a, Iterable):
                        if '?' in a or '*' in a:
                            alist = glob.glob(a)
                            alist.sort()
                            if len(alist) > 0:
                                newa = []
                                for c in alist:
                                    try:
                                        c = self.filehandler.load(c)
                                    except:
                                        pass
                                    newa.append(c)
                            else:
                                try:
                                    newa = self.filehandler.load(a)
                                except:
                                    newa = a
                        else:
                            try:
                                newa = self.filehandler.load(a)
                            except:
                                newa = a
                    else:
                        try:
                            newa = self.filehandler.load(a)
                        except:
                            newa = a
                newargs.append(newa)
        else:
            newargs = args
            try:
                newargs = self.filehandler.load(newargs)
            except:
                pass
        return newargs

    def submit(self, func, *args):
        """
        Wrapper round the dask submit() method, so that a tuple of
        futures, rather than just one future, is returned.

        args:
            func (function/kernel): the function to be run
            args (list): the function arguments
        returns:
            future or tuple of futures
        """
        newargs = self._filehandlify(args)
        if isinstance(func, SubprocessKernel):
            future = self.client.submit(func.run, *newargs, pure=False)
            return self.unpack(func, future)
        if isinstance(func, FunctionKernel):
            future = self.client.submit(func.run, *newargs, pure=False)
            return self.unpack(func, future)
        else:
            return self.client.submit(func, *args)

    def _lt2tl(self, l):
        '''converts a list of tuples to a tuple of lists'''
        result = []
        for i in range(len(l[0])):
            result.append([t[i] for t in l])
        return tuple(result)

    def map(self, func, *iterables):
        """
        Wrapper arounf the dask map() method so it returns lists of
        tuples of futures, rather than lists of futures.

        args:
            func (function): the function to be mapped
            iterables (iterables): the function arguments

        returns:
            list or tuple of lists: futures returned by the mapped function
        """
        its = []
        maxlen = 0
        for iterable in iterables:
            if isinstance(iterable, list):
                l = len(iterable)
                if l > maxlen:
                    maxlen = l
        for iterable in iterables:
            if isinstance(iterable, list):
                l = len(iterable)
                if l != maxlen:
                    raise ValueError('Error: not all iterables are same length')
                its.append(iterable)
            else:
                its.append([iterable] * maxlen)
        newits = self._filehandlify(its)
        if isinstance(func, SubprocessKernel):
            futures = self.client.map(func.run, *newits, pure=False)
            result = [self.unpack(func, future) for future in futures]
        elif isinstance(func, FunctionKernel):
            futures = self.client.map(func.run, *newits, pure=False)
            result = [self.unpack(func, future) for future in futures]
        else:
            result =  self.client.map(func, *its, pure=False)
        if isinstance(result[0], tuple):
            result = self._lt2tl(result)
        return result
