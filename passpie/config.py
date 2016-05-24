# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
import os

import yaml

from .utils import tempdir
from .crypt import ensure_keys, import_keys, get_default_recipient
from ._compat import *


HOMEDIR = os.path.expanduser("~")
DEFAULT_CONFIG_PATH = os.path.join(os.path.join(HOMEDIR, '.passpierc'))
DEFAULT = {
    'path': os.path.join(os.path.join(HOMEDIR, '.passpie')),
    'key_length': 4096,
    'genpass_pattern': r'[a-z]{10} [-_+=*&%$#]{10} [A-Z]{10}',
    'homedir': os.path.join(os.path.expanduser('~/.gnupg')),
    'recipient': None,
    'table_format': 'fancy_grid',
    'headers': ['name', 'login', 'password', 'comment'],
    'colors': {'name': 'yellow', 'login': 'green'},
    'repo': True,
    'autopull': None,
    'autopush': None,
    'status_repeated_passwords_limit': 5,
    'copy_timeout': 0,
    'extension': '.pass',
    'recipient': None,
    'hidden': ['password'],
    'encrypted': ['password'],
    'hidden_string': u'********',
    'aliases': {"rm": "remove"},
}


def default():
    return deepcopy(DEFAULT)


def read(path, filename='.config'):
    try:
        if path and os.path.isdir(path) and ".config" in os.listdir(path):
            path = os.path.join(path, '.config')
        with open(path) as config_file:
            content = config_file.read()
        return yaml.load(content)
    except (IOError, TypeError):
        logging.debug(u'config file "{}" not found'.format(path))
    except yaml.scanner.ScannerError as e:
        logging.error(u'Malformed user configuration file: {}'.format(e))

    return {}


def create(config_path, overrides):
    values = {}
    values.update(overrides)
    with open(config_path, 'w') as config_file:
        config_file.write(yaml.dump(values, default_flow_style=False))


def from_path(config_path, overrides=None):
    overrides = overrides if overrides else {}
    cfg = deepcopy(DEFAULT)
    cfg.update(read(DEFAULT_CONFIG_PATH))
    cfg.update(read(config_path))
    cfg.update(overrides)
    return cfg


def setup_crypt(configuration):
    configuration = deepcopy(configuration)
    keys_filepath = ensure_keys(configuration['path'])
    if keys_filepath:
        configuration['homedir'] = tempdir()
        import_keys(keys_filepath, configuration['homedir'])
    if not configuration['recipient']:
        configuration['recipient'] = get_default_recipient(configuration['homedir'])
    return configuration
