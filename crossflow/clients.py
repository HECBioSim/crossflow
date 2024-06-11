"""
Clients.py: thin wrapper over dask client
"""
import glob
import pickle
import sys
from dask.distributed import Client as DaskClient
try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable
from dask.distributed import Future
from .tasks import FunctionTask, SubprocessTask
from .filehandling import FileHandler
from . import config


class Client(DaskClient):
    """Thin wrapper around Dask client so functions that return multiple
    values (tuples) generate tuples of futures rather than single futures.
    """

    def __init__(self, *args, **kwargs):
        self.filehandler = FileHandler(config.stage_point)
        super().__init__(*args, **kwargs)

    def upload(self, some_object):
        """
        Upload some data/object to the.workers

        args:
            some_object (any type): what to upload

        returns:
            dask.Future
        """
        try:
            some_object = self.filehandler.load(some_object)
        except IOError:
            pass
        return self.scatter(some_object, broadcast=True)

    def _rough_size(self, item):
        """
        Get the approximate size of an item, to decide if
        it should be uploaded to the workers in advance

        """
        x = pickle.dumps(item)
        return sys.getsizeof(x)

    def _futurize(self, item):
        """
        Upload an item, if it's not already a Future

        """
        if isinstance(item, Future):
            return item
        else:
            if isinstance(item, list):
                for i, j in enumerate(item):
                    if not isinstance(j, Future):
                        if self._rough_size(j) > 10000:
                            item[i] = self.upload(j)
                return item
            else:
                if self._rough_size(item) > 10000:
                    return self.upload(item)
                else:
                    return item

    def _unpack(self, task, future):
        """
        Unpacks the single future returned by task when run through
        a dask submit() or map() method, returning a tuple of futures.

        The outputs attribute of task lists how many values task
        should properly return.

        args:
            task (Task): the task that generated the future
            future (Future): the future returned by task

        returns:
            future or tuple of futures.
        """
        if len(task.outputs) == 1:
            return future
        outputs = []
        for i in range(len(task.outputs)):
            outputs.append(self.submit(lambda tup, j: tup[j], future, i))
        return tuple(outputs)

    def _filehandlify(self, args):
        """
        work through an argument list, converting paths to filehandles
        where possible.
        """
        if isinstance(args, Iterable):
            newargs = []
            for a in args:
                if isinstance(a, list):
                    newa = []
                    for b in a:
                        if isinstance(b, Iterable):
                            if "?" in b or "*" in b:
                                blist = glob.glob(b)
                                blist.sort()
                                if len(blist) > 0:
                                    newb = []
                                    for c in blist:
                                        try:
                                            c = self.filehandler.load(c)
                                        except IOError:
                                            pass
                                        newb.append(c)
                                else:
                                    try:
                                        newb = self.filehandler.load(b)
                                    except IOError:
                                        newb = b
                            else:
                                try:
                                    newb = self.filehandler.load(b)
                                except IOError:
                                    newb = b
                        else:
                            try:
                                newb = self.filehandler.load(b)
                            except IOError:
                                newb = b

                        newa.append(newb)
                else:
                    if isinstance(a, Iterable):
                        if "?" in a or "*" in a:
                            alist = glob.glob(a)
                            alist.sort()
                            if len(alist) > 0:
                                newa = []
                                for c in alist:
                                    try:
                                        c = self.filehandler.load(c)
                                    except IOError:
                                        pass
                                    newa.append(c)
                            else:
                                try:
                                    newa = self.filehandler.load(a)
                                except IOError:
                                    newa = a
                        else:
                            try:
                                newa = self.filehandler.load(a)
                            except IOError:
                                newa = a
                    else:
                        try:
                            newa = self.filehandler.load(a)
                        except IOError:
                            newa = a
                newargs.append(newa)
        else:
            newargs = args
            try:
                newargs = self.filehandler.load(newargs)
            except IOError:
                pass
        return newargs

    def submit(self, func, *args, **kwargs):
        """
        Wrapper round the dask submit() method, so that a tuple of
        futures, rather than just one future, is returned.

        args:
            func (function/task): the function to be run
            args (list): the function arguments
            kwargs (dict): keyword arguments to submit()
        returns:
            future or tuple of futures
        """
        newargs = self._filehandlify(args)
        if isinstance(newargs, list):
            for i, arg in enumerate(newargs):
                newargs[i] = self._futurize(arg)
        else:
            newargs = self._futurize(newargs)

        if isinstance(func, (SubprocessTask, FunctionTask)):
            kwargs['pure'] = False
            future = super().submit(func.run, *newargs, **kwargs)
            return self._unpack(func, future)
        else:
            return super().submit(func, *args, **kwargs)

    def _lt2tl(self, tuplist):
        """converts a list of tuples to a tuple of lists"""
        result = []
        for i in range(len(tuplist[0])):
            result.append([t[i] for t in tuplist])
        return tuple(result)

    def map(self, func, *iterables, **kwargs):
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
            if isinstance(iterable, (list, tuple)):
                n_items = len(iterable)
                if n_items > maxlen:
                    maxlen = n_items
        for iterable in iterables:
            if isinstance(iterable, (list, tuple)):
                n_items = len(iterable)
                if n_items != maxlen:
                    raise ValueError(
                        "Error: not all iterables are same length"
                    )
                its.append(iterable)
            else:
                its.append([iterable] * maxlen)

        kwargs['pure'] = False
        if isinstance(func, (SubprocessTask, FunctionTask)):
            newits = self._filehandlify(its)
            for i, arg in enumerate(newits):
                newits[i] = self._futurize(arg)

            #futures = super().map(func, *newits, **kwargs)
            futures = [super().submit(func, *newit, **kwargs) for newit in zip(*newits)]
            result = [self._unpack(func, future) for future in futures]
        else:
            #result = super().map(func, *its, **kwargs)
            result = [super().submit(func, *it, **kwargs) for it in zip(*its)]
        if isinstance(result[0], tuple):
            result = self._lt2tl(result)
        return result
