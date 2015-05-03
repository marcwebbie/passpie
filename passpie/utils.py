from argparse import Namespace
from contextlib import contextmanager
from pkg_resources import get_distribution, DistributionNotFound
import errno
import logging
import os
import random
import string

import yaml


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


def load_config(default_config, user_config_path):
    if os.path.exists(user_config_path) and os.path.isfile(user_config_path):
        with open(user_config_path) as config_file:
            config_content = config_file.read()

        try:
            user_config = yaml.load(config_content)
            default_config.update(user_config)
        except yaml.scanner.ScannerError as e:
            logging.debug('Malformed user configuration file {}'.format(e))

    config = Namespace(**default_config)
    return config
