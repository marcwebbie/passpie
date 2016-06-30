import os
import sys
try:
    from shutil import which as _which
except ImportError:
    from distutils.spawn import find_executable as _which

try:
    basestring = basestring
except NameError:
    basestring = str

try:
    unicode = unicode
except NameError:
    unicode = str


def which(binary):
    path = _which(binary)
    if path:
        realpath = os.path.realpath(path)
        return realpath
    return None


def is_python2():
    return sys.version_info < (3,)


class FileNotFoundError(OSError):

    def __init__(self, message="No such file or directory"):
        super(FileNotFoundError, self).__init__(2, message)


class FileExistsError(OSError):

    def __init__(self, message="File exists"):
        super(FileExistsError, self).__init__(17, message)
