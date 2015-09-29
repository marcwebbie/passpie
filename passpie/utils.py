from contextlib import contextmanager
from pkg_resources import get_distribution, DistributionNotFound
from random import SystemRandom
import copy
import errno
import logging
import os
import shutil
import string
import tempfile

import yaml

from ._compat import which


import_module = __import__

logger = logging.getLogger('passpie')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(name)s::%(levelname)s::%(module)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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


def read_config(path):
    try:
        with open(path) as config_file:
            content = config_file.read()
    except IOError:
        logger.debug('config file "%s" not found' % path)
    return content if content else {}


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
