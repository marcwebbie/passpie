from __future__ import unicode_literals
import re

from tinydb import Storage, TinyDB, Query
from tinydb.storages import touch
from tinydb.middlewares import CachingMiddleware
from faker import Faker
import yaml

from .git import Repo
from .utils import safe_join, logger
from .gpg import GPG
from .config import Config


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

    @classmethod
    def build(cls, **kwargs):
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
        return values


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
    fullname = u"{}@{}".format("" if login is None else login, name)
    return fullname


class YAMLStorage(Storage):
    def __init__(self, filename):
        self.filename = filename
        touch(self.filename)

    def as_dict(self, data):
        if data:
            for table_name in data:
                table = data[table_name]
                for element_id in table:
                    table[element_id] = dict(table[element_id])
        return data

    def read(self):
        logger.info("read credentials:%s", self.filename)
        with open(self.filename) as handle:
            try:
                data = yaml.load(handle.read())  # (2)
                return data
            except yaml.YAMLError:
                return None  # (3)

    def write(self, data):
        logger.info("write credentials:%s", self.filename)
        data = self.as_dict(data)
        with open(self.filename, 'w') as handle:
            yaml.safe_dump(data, handle, default_flow_style=False)


class Database(TinyDB):
    """Credentials database class"""

    def __init__(self, path):
        self.path = path
        self.repo = Repo(self.path)
        self.cfg = Config(safe_join(path, "config.yml"))
        self.gpg = GPG(
            safe_join(path, "keys.asc"),
            recipient=self.cfg['GPG_RECIPIENT'],
            default_homedir=self.cfg['GPG_HOMEDIR'],
        )

        super(Database, self).__init__(
            safe_join(path, "credentials.yml"),
            storage=CachingMiddleware(YAMLStorage),
            default_table="credentials",
        )

    def close(self):
        self.cfg.write()
        super(Database, self).close()

    @classmethod
    def query(cls, fullname):
        """Generate a search query spliting fullname into
        login and name"""
        login, name = split_fullname(fullname)
        if login:
            return (Query().name == name) & (Query().login == login)
        else:
            return (Query().name == name)
