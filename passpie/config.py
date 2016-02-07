import copy
import logging
import os
import re

import yaml

from .utils import tempdir
from .crypt import ensure_keys, import_keys, get_default_recipient
from .history import clone


HOMEDIR = os.path.expanduser("~")
DEFAULT_CONFIG_PATH = os.path.join(os.path.join(HOMEDIR, '.passpierc'))
DEFAULT = {
    'path': os.path.join(os.path.join(HOMEDIR, '.passpie')),
    'short_commands': False,
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
    'recipient': None
}


def is_repo_url(path):
    if path:
        return re.match(
            r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?',
            path
        ) is not None


def read(path, filename='.config'):
    try:
        with open(os.path.join(path, '.config')) as config_file:
            content = config_file.read()
        configuration = yaml.load(content)
    except IOError:
        logging.debug('config file "%s" not found' % path)
        return {}
    except yaml.scanner.ScannerError as e:
        logging.error('Malformed user configuration file: {}'.format(e))
        return {}
    return configuration


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


def load(**overrides):
    database_path = os.path.expanduser(overrides.get('path', DEFAULT['path']))
    configuration = copy.deepcopy(DEFAULT)

    configuration.update(read(DEFAULT_CONFIG_PATH))   # 1. Global configuration
    configuration.update(read(database_path))         # 2. Local configuration
    configuration.update(overrides)                   # 3. Command line options

    if is_repo_url(configuration['path']) is True:
        temporary_path = clone(configuration['path'], depth="1")
        configuration.update(read(temporary_path))  # Read cloned config
        configuration['path'] = temporary_path

    configuration = setup_crypt(configuration)
    return configuration
