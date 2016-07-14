import sys


if sys.version_info < (3,):
    # python 2
    bytes = str
    str = unicode


class unicode_str(str):
    pass


class bytes_str(bytes):
    pass


class FileNotFoundError(OSError):

    def __init__(self, message="No such file or directory"):
        super(FileNotFoundError, self).__init__(2, message)


class FileExistsError(OSError):

    def __init__(self, message="File exists"):
        super(FileExistsError, self).__init__(17, message)
