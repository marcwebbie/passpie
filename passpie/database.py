import re

from tinydb import Storage, TinyDB, Query
from tinydb.storages import touch
from faker import Faker
import yaml

from .git import Repo
from .utils import safe_join


class CredentialFactory(dict):
    def __init__(self, **kwargs):
        faker = Faker()
        fullname = kwargs.pop("fullname", None)
        if fullname is not None:
            login, name = split_fullname(fullname)
            kwargs["login"] = login
            kwargs["name"] = name
        values = {
            "login": kwargs.get('login', faker.user_name()),
            "name": kwargs.get('name', faker.domain_name()),
            "password": kwargs.get('password', faker.password(length=32)),
            "comment": kwargs.get('comment', faker.sentence(nb_words=3)),
        }
        super(CredentialFactory, self).__init__(**values)


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

    def __init__(self, archive, config, gpg):
        self.archive = archive
        self.path = archive.path
        self.config = config
        self.gpg = gpg
        self.passphrase = gpg.passphrase
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
        if self.archive.format == "git" and self.config["GIT_PUSH"]:
            self.repo.push()

    def close(self):
        self.write()

    def encrypt(self, credential):
        credential["password"] = self.gpg.encrypt(credential["password"])
        return credential

    def decrypt(self, credential):
        credential["password"] = self.gpg.decrypt(credential["password"])
        return credential
