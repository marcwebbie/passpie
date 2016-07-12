from copy import deepcopy
import os

from .utils import safe_join, yaml_to_python, yaml_dump, yaml_load


class Config(dict):

    GLOBAL_PATH = safe_join("~", ".passpierc")

    DEFAULT = {
        # Database
        'DATABASE': "passpie.db",
        'GIT': True,
        'GIT_PUSH': None,

        # GPG
        'KEY_LENGTH': 4096,
        'HOMEDIR': None,
        'RECIPIENT': None,

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
        'PASSWORD_PATTERN': "[a-zA-Z0-9=+_*!?&%$# ]{32}",
        'PASSWORD_RANDOM': False,

        # Cli
        'VERBOSE': False,
        'DEBUG': False,
    }

    def __init__(self, path):
        self.path = path
        self.inital_data = yaml_load(self.path)
        self.data = self.get_global(self.inital_data)
        super(Config, self).__init__(**self.data)

    def write(self):
        return yaml_dump(self.get_local(), self.path)

    @classmethod
    def get_global(cls, overrides={}):
        global_config = deepcopy(cls.DEFAULT)
        global_config.update(yaml_load(Config.GLOBAL_PATH))
        for k in global_config.keys():
            environ_name = "PASSPIE_{}".format(k.upper())
            environ_value = os.environ.get(environ_name)
            if environ_value:
                global_config[k] = yaml_to_python(environ_value)
        global_config.update(overrides)
        return global_config

    def get_local(self):
        modified_values = {}
        for key, value in self.items():
            if self.get(key) != self.DEFAULT.get(key):
                modified_values[key] = value
        return modified_values
