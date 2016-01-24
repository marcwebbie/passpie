import copy
import logging
import os

import yaml

from .utils import tempdir
from .crypt import ensure_keys, import_keys, get_default_recipient


DEFAULT_PATH = os.path.join(os.path.expanduser('~/.passpierc'))
DEFAULT = {
    'path': os.path.join(os.path.expanduser('~/.passpie')),
    'short_commands': False,
    'key_length': 4096,
    'genpass_length': 32,
    'genpass_symbols': "_-#|+=",
    'homedir': os.path.join(os.path.expanduser('~/.gnupg')),
    'recipient': 'passpie@local',
    'table_format': 'fancy_grid',
    'headers': ['name', 'login', 'password', 'comment'],
    'colors': {'name': 'yellow', 'login': 'green'},
    'repo': True,
    'status_repeated_passwords_limit': 5,
    'copy_timeout': 0,
    'extension': '.pass',
    'recipient': None
}


def read(path):
    try:
        with open(path) as config_file:
            content = config_file.read()
        config = yaml.load(content)
    except IOError:
        logging.debug('config file "%s" not found' % path)
        return DEFAULT
    except yaml.scanner.ScannerError:
        logging.error('Malformed user configuration file: {}'.format(path))
        return {}

    return config


def read_global_config():
    return read(DEFAULT_PATH)


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
    database_path = overrides.get('path', DEFAULT['path'])
    local_config_path = os.path.join(os.path.expanduser(database_path), '.config')
    configuration = copy.deepcopy(DEFAULT)
    if os.path.exists(DEFAULT_PATH):
        configuration.update(read_global_config())
    if os.path.exists(local_config_path):
        configuration.update(read(local_config_path))
    if overrides:
        configuration.update(overrides)

    configuration = setup_crypt(configuration)
    return configuration
