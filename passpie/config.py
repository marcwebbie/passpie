import copy
import logging
import os

import yaml


DEFAULT_PATH = os.path.join(os.path.expanduser('~/.passpierc'))
DEFAULT = {
    'path': DEFAULT_PATH,
    'short_commands': False,
    'key_length': 4096,
    'genpass_length': 32,
    'genpass_symbols': "_-#|+=",
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


def load(path, **overrides):
    local_config_path = os.path.join(os.path.expanduser(path), '.config')
    configuration = copy.deepcopy(DEFAULT)
    if os.path.exists(DEFAULT_PATH):
        configuration.update(read_global_config())
    if os.path.exists(local_config_path):
        configuration.update(read(local_config_path))
    if overrides:
        configuration.update(overrides)
    return configuration
