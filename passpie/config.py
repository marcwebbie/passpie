# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
import os

import yaml

from .utils import tempdir, mkdir_open, mkdir
from .crypt import ensure_keys, import_keys, get_default_recipient
from ._compat import *


HOMEDIR = os.path.expanduser("~")
DEFAULT_CONFIG_PATH = os.path.join(os.path.join(HOMEDIR, '.passpierc'))
DEFAULT = {
    'path': os.path.join(os.path.join(HOMEDIR, '.passpie')),
    'url': None,
    'key_length': 4096,
    'passphrase': None,
    'private': False,
    'genpass_pattern': r'[a-z]{10} [-_+=*&%$#]{10} [A-Z]{10}',
    'homedir': os.path.join(os.path.expanduser('~/.gnupg')),
    'recipient': None,
    'table_format': 'fancy_grid',
    'headers': ['name', 'login', 'password', 'comment'],
    'colors': {'name': 'yellow', 'login': 'green'},
    'repo': True,
    'autopull': None,
    'autopush': "origin/master",
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


def read(path):
    try:
        with open(path) as config_file:
            content = config_file.read()
        return yaml.load(content)
    except (IOError, TypeError):
        logging.debug(u'config file "{}" not found'.format(path))
    except yaml.scanner.ScannerError as e:
        logging.error(u'Malformed user configuration file: {}'.format(e))
    return {}


def create(config_path, overrides=None):
    values = {}
    if isinstance(overrides, dict):
        values.update(overrides)
    mkdir(os.path.dirname(config_path))
    with open(config_path, 'w') as config_file:
        config_file.write(yaml.safe_dump(values, default_flow_style=False))


def setup_crypt(configuration):
    configuration = deepcopy(configuration)
    keys_filepath = ensure_keys(configuration['path'])
    if keys_filepath:
        configuration['homedir'] = tempdir()
        import_keys(keys_filepath, configuration['homedir'])
    if not configuration['recipient']:
        configuration['recipient'] = get_default_recipient(configuration['homedir'])
    return configuration


def load(extra_config):
    """
    CONFIG LOAD ORDER

    1) DEFAULT_CONFIG
    2) .passpierc
    3) .config from path on passpierc
    4) extra_config
    5) if path in extra_conif, .config from it
    """
    cfg = deepcopy(DEFAULT)  # 1)
    cfg.update(read(DEFAULT_CONFIG_PATH))  # 2)
    cfg.update(read(os.path.join(cfg["path"], ".config")))  # 3)
    cfg.update(extra_config)  # 4)
    if extra_config.get("path"):  # 5)
        cfg.update(read(os.path.join(extra_config["path"], ".config")))
    return setup_crypt(cfg)
