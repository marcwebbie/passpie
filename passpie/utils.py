from contextlib import contextmanager
import errno
import os
import re
from random import SystemRandom
import tempfile

from rstr import Rstr

from ._compat import which

rstr = Rstr(SystemRandom())


import_module = __import__


def genpass(pattern=r'[\w]{32}'):
    """generates a password with random chararcters
    """
    try:
        return rstr.xeger(pattern)
    except re.error as e:
        raise ValueError(str(e))


@contextmanager
def mkdir_open(path, mode="r"):
    try:
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise
    with open(path, mode) as fd:
        yield fd


def ensure_dependencies():
    try:
        assert which('gpg') or which('gpg2')
    except AssertionError:
        raise RuntimeError('GnuPG not installed. https://www.gnupg.org/')


def tempdir():
    return tempfile.mkdtemp()


def touch(path):
    with open(path, "w"):
        pass
