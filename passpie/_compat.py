import sys

try:
    basestring
except NameError:
    basestring = str

try:
    unicode = unicode
except NameError:
    unicode = str


def is_python2():
    return sys.version_info < (3,)


class FileNotFoundError(OSError):

    def __init__(self, message="No such file or directory"):
        super(FileNotFoundError, self).__init__(2, message)


class FileExistsError(OSError):

    def __init__(self, message="File exists"):
        super(FileExistsError, self).__init__(17, message)
