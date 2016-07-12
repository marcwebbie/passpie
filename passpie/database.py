import re

from tinydb import Storage, TinyDB, Query
from tinydb.storages import touch
import factory
import yaml

from .git import Repo
from .utils import safe_join
from .config import Config
from .gpg import GPG


class CredentialFactory(factory.Factory):
    class Meta:
        model = dict

    login = factory.Faker('user_name')
    name = factory.Faker('domain_name')
    password = factory.Faker('password', length=32)
    comment = factory.Faker('sentence', nb_words=2)


def split_fullname(fullname):
    regex = re.compile(r'(?:(?P<login>.+?(?:\@.+?)?)@(?P<name>.+?$))')
    regex_name_only = re.compile(r'(?P<at>@)?(?P<name>.+?$)')

    if regex.match(fullname):
        mobj = regex.match(fullname)
    elif regex_name_only.match(fullname):
        mobj = regex_name_only.match(fullname)
    else:
        raise ValueError("not a valid fullname: {}".format(fullname))

    match_dict = mobj.groupdict()
    login = match_dict.get('login', "")
    name = match_dict.get("name")

    return login, name


def make_fullname(login, name):
    fullname = "{}@{}".format("" if login is None else login, name)
    return fullname


class YAMLStorage(Storage):
    def __init__(self, filename):
        self.filename = filename
        touch(self.filename)

    def read(self):
        with open(self.filename) as handle:
            try:
                data = yaml.load(handle.read())  # (2)
                return data
            except yaml.YAMLError:
                return None  # (3)

    def write(self, data):
        for table_name in data:
            table = data[table_name]
            for element_id in table:
                table[element_id] = dict(table[element_id])

        with open(self.filename, 'w') as handle:
            yaml.safe_dump(data, handle, default_flow_style=False)


class Database(TinyDB):

    def __init__(self, archive, passphrase):
        self.archive = archive
        self.path = archive.path
        self.gpg = GPG(safe_join(archive.path, "keys.yml"), passphrase)
        self.config = Config(safe_join(archive.path, "config.yml"))
        self.repo = Repo(self.path)
        super(Database, self).__init__(
            safe_join(self.path, "credentials.yml"), storage=YAMLStorage)

    @classmethod
    def query(cls, fullname):
        login, name = split_fullname(fullname)
        if login:
            return (Query().name == name) & (Query().login == login)
        else:
            return (Query().name == name)

    def write(self):
        self.gpg.write()
        self.config.write()
        if self.config["GIT_PUSH"]:
            self.repo.push()

    def close(self):
        self.write()

    def encrypt(self, credential):
        credential["password"] = self.gpg.encrypt(credential["password"])
        return credential

    def decrypt(self, credential):
        credential["password"] = self.gpg.decrypt(credential["password"])
        return credential
