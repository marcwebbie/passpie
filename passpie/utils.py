from contextlib import contextmanager
from random import SystemRandom
import errno
import os
import shutil
import string
import tempfile

from ._compat import which


import_module = __import__


def genpass(length=32, special="_-#|+="):
    """generates a password with random chararcters
    """
    chars = special + string.ascii_letters + string.digits + " "
    return "".join(SystemRandom().choice(chars) for _ in range(length))


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


@contextmanager
def tempdir():
    path = tempfile.mkdtemp()
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)


def touch(path):
    with open(path, "w"):
        pass
