# -*- coding: utf-8 -*-
import logging
import os
import re

import yaml

from .utils import tempdir
from .crypt import ensure_keys, import_keys, get_default_recipient


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
    'hidden_string': u'********'
}


def is_repo_url(path):
    if path:
        return re.match(
            r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?',
            path
        ) is not None


def read(path, filename='.config'):
    try:
        if os.path.isdir(path):
            path = os.path.join(path, '.config')
        with open(path) as config_file:
            content = config_file.read()
        configuration = yaml.load(content)
    except IOError:
        logging.debug(u'config file "{}" not found'.format(path))
        return {}
    except yaml.scanner.ScannerError as e:
        logging.error(u'Malformed user configuration file: {}'.format(e))
        return {}
    return configuration or {}


def create(path, defaults={}, filename='.config'):
    config_path = os.path.join(os.path.expanduser(path), filename)
    with open(config_path, 'w') as config_file:
        config_file.write(yaml.dump(defaults, default_flow_style=False))


def setup_crypt(configuration):
    keys_filepath = ensure_keys(configuration['path'])
    if keys_filepath:
        configuration['homedir'] = tempdir()
        import_keys(keys_filepath, configuration['homedir'])
    if not configuration['recipient']:
        configuration['recipient'] = get_default_recipient(configuration['homedir'])
    return configuration
