from contextlib import contextmanager
from pkg_resources import get_distribution, DistributionNotFound
import errno
import os
import random
import string


def genpass(length=32, special="_-#|+="):
    """generates a password with random chararcters
    """
    chars = special + string.ascii_letters + string.digits + " "
    return "".join(random.choice(chars) for _ in range(length))


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


def get_version():
    try:
        _dist = get_distribution('passpie')
        dist_loc = os.path.normcase(_dist.location)
        here = os.path.normcase(__file__)
        if not here.startswith(os.path.join(dist_loc, 'passpie')):
            raise DistributionNotFound
    except DistributionNotFound:
        return 'Please install this project with setup.py or pip'
    else:
        return _dist.version
