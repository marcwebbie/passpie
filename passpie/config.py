from copy import deepcopy
import os

from .utils import safe_join, yaml_to_python, yaml_dump, yaml_load
from .gpg import DEFAULT_EMAIL


def with_environ(dictionary, prefix):
    dictionary = deepcopy(dictionary)
    for key in dictionary.keys():
        variable_name = "{}{}".format(prefix, key)
        environ_value = os.environ.get(variable_name)
        if environ_value:
            dictionary[key] = yaml_to_python(environ_value)
    return dictionary


class Config(object):

    GLOBAL_PATH = safe_join("~", ".passpierc")

    DEFAULT = {
        # Database
        'DATABASE': "passpie.db",
        'GIT': True,
        'GIT_PUSH': None,

        # GPG
        'KEY_LENGTH': 4096,
        'GPG_HOMEDIR': None,
        'GPG_RECIPIENT': DEFAULT_EMAIL,

        # Table
        'TABLE_FORMAT': 'fancy_grid',
        'TABLE_SHOW_PASSWORD': False,
        'TABLE_HIDDEN_STRING': u'********',
        'TABLE_FIELDS': ('name', 'login', 'password', 'comment'),
        'TABLE_STYLE': {
            'login': {"fg": 'green'},
            'name': {"fg": 'yellow'}
        },

        # Credentials
        'COPY_TIMEOUT': 0,
        'PASSWORD_PATTERN': None,
        'PASSWORD_RANDOM': False,
        'PASSWORD_RANDOM_LENGTH': 32,

        # Cli
        'VERBOSE': False,
        'DEBUG': False,
    }

    def __init__(self, path, overrides={}):
        self.path = path
        self.custom = yaml_load(path)
        self.overrides = overrides
        self.overrides.update(deepcopy(self.custom))
        self.data = self.get_global(self.overrides)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.custom[key] = value

    def keys(self):
        return self.data.keys()

    @classmethod
    def get_global(cls, overrides={}):
        cfg = deepcopy(cls.DEFAULT)
        cfg.update(yaml_load(cls.GLOBAL_PATH))
        cfg.update(deepcopy(overrides))
        cfg.update(with_environ(cfg, "PASSPIE_"))
        return cfg

    def get_local(self):
        return {key: self.data[key] for key in self.custom.keys()}

    def write(self, path=None):
        path = path if path else self.path
        yaml_dump(self.get_local(), path)
