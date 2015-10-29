import copy
import logging
import os

import yaml

from . import crypt


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.passpierc')
DB_DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.passpie')
DEFAULT_CONFIG = {
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
    'recipient': None,
    'homedir': crypt.GPG_HOMEDIR
}


def read_config(path):
    try:
        with open(path) as config_file:
            content = config_file.read()
        config = yaml.load(content)
    except IOError:
        logging.debug('config file "%s" not found' % path)
        return {}
    except yaml.scanner.ScannerError as e:
        logging.error('Malformed user configuration file {}'.format(e))
        return {}

    return config


def create(path, **kwargs):
    with open(os.path.expanduser(path), 'w') as config_file:
        config_file.write(yaml.dump(kwargs, default_flow_style=False))


def create_default(path):
    with open(os.path.expanduser(path), 'w') as config_file:
        config_file.write(yaml.dump(DEFAULT_CONFIG, default_flow_style=False))


def load(database_path):
    config = copy.deepcopy(DEFAULT_CONFIG)
    global_config = read_config(DEFAULT_CONFIG_PATH)
    local_config = read_config(os.path.join(database_path, '.config'))
    config.update(global_config)
    config.update(local_config)
    return config
