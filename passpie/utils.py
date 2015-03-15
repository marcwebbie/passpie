from contextlib import contextmanager
import errno
import os
import random
import string


def genpass(length=32, special="_-#|+="):
    """generates a password with random chararcters
    """
    chars = "{}{}{}{}{}".format(
        special,
        string.ascii_uppercase,
        string.digits,
        string.ascii_lowercase,
        string.whitespace)
    return "".join(random.SystemRandom().choice(chars) for _ in range(length))


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
