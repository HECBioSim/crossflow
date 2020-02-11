'''
filehanding.py: this module provides classes for passing files between
processes on distributed computing platforms that may not share a common
file system.
'''

import os
import zlib
import os.path as op
import uuid
import fsspec

'''
This module defines classes to handle files in distributed environments
where filesyatems may not be shared.

Objects of each class are instantiated with the path of an existing file on
an existing file syatem:

    fh = FileHandle('/path/to/file')

and have a save() method that creates a local copy of that file:

    filename_here = fh.save(filename_here)

and also an as_file() method which returns a path that points at a (maybe temporary) copy of the file contents, suitable for use in cases where a function requires a filename:

    with open(fh.as_file()) as f:
        ...

'''
class FileHandler(object):
    def __init__(self, stage_point=None):
        self.stage_point = stage_point

    def load(self, path):
        return FileHandle(path, self.stage_point)

class FileHandle(object):
    '''
    A portable container for a file.
    '''
    def __init__(self, path, stage_point):
        source = fsspec.open(path)
        ext = os.path.splitext(path)[1]
        self.path = path
        self.uid = str(uuid.uuid4()) + ext
        if stage_point is None:
            self.staging_path = None
            with source as s:
                self.store = zlib.compress(s.read())
        else:
            self.staging_path = op.join(stage_point, self.uid)
            self.store = fsspec.open(self.staging_path, 'wb', compression='bz2')
            with source as s:
                with self.store as d:
                    d.write(s.read())
            source.close()
            self.store.close()
            self.store.mode = 'rb'
   
    def __str__(self):
        return "Filehandle for file {} at {}".format(self.path, self.staging_path)

    def save(self, path):
        """
        Save the file

        args:
            path (str): file path

        returns:
            str: the path
        """
        source = self.store
        #source.mode = 'rb'
        dest = fsspec.open(path, 'wb')
        if self.staging_path is None:
            with dest as d:
                d.write(zlib.decompress(source))
        else:
            with source as s:
                with dest as d:
                    d.write(s.read())
        dest.close()
        return path
            
    def as_file(self):
        """
        Returns a path on the current local file system which points at the file
        """
        dest = os.path.join(os.environ['TMPDIR'], self.uid)
        return self.save(dest)

