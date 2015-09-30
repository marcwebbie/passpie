import copy
import logging
import os

import yaml


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.passpierc')
DB_DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.passpie')
DEFAULT_CONFIG = {
    'path': DB_DEFAULT_PATH,
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


def create(path, default=True, **kwargs):
    config_path = os.path.join(os.path.expanduser(path), '.passpierc')
    with open(config_path, 'w') as config_file:
        if default:
            config_file.write(yaml.dump(DEFAULT_CONFIG, default_flow_style=False))
        else:
            config_file.write(yaml.dump(kwargs, default_flow_style=False))


def load():
    if not os.path.isfile(DEFAULT_CONFIG_PATH):
        create(DEFAULT_CONFIG_PATH, default=True)
    global_config = read_config(DEFAULT_CONFIG_PATH)
    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(global_config)
    local_config = read_config(os.path.join(config['path'], '.passpierc'))
    config.update(local_config)
    return config
