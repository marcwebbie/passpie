from copy import deepcopy
import os
import re

from tinydb import TinyDB, Query

from .gpg import GPG
from .repo import Repository, clone
from .utils import is_repo_url


def split_fullname(fullname):
    regex = re.compile(r'(?:(?P<login>.+?(?:\@.+?)?)@(?P<name>.+?$))')
    regex_name_only = re.compile(r'(?P<at>@)?(?P<name>.+?$)')

    if regex.match(fullname):
        mobj = regex.match(fullname)
    elif regex_name_only.match(fullname):
        mobj = regex_name_only.match(fullname)
    else:
        raise ValueError("Not a valid name")

    if mobj.groupdict().get('at'):
        login = ""
    else:
        login = mobj.groupdict().get('login')
    name = mobj.groupdict().get("name")

    return login, name


def make_fullname(login, name):
    fullname = "{}@{}".format("" if login is None else login, name)
    return fullname


class Database(TinyDB):

    def __init__(self, cfg, passphrase):
        self.cfg = cfg
        self.passphrase = passphrase
        url = None

        self.path = self.cfg["path"]
        super(Database, self).__init__(
            os.path.join(self.cfg["path"], "credentials.json"),
            default_table="credentials"
        )

    def keys(self):
        private = self.table("keys").get(Query().private == True)
        public = self.table("keys").get(Query().private == False)
        if private and public:
            return public["text"], private["text"]

    def insert_keys(self, public, private):
        self.table("keys").insert({"private": False, "text": public})
        self.table("keys").insert({"private": True, "text": private})

    def query(self, fullname):
        login, name = split_fullname(fullname)
        if login:
            return (Query().name == name) & (Query().login == login)
        else:
            return (Query().name == name)

    def encrypt_fields(self, credential):
        credential = deepcopy(credential)
        for field in self.cfg["encrypted"]:
            credential[field] = self.gpg.encrypt(credential[field])
        return credential

    def decrypt_fields(self, credential):
        credential = deepcopy(credential)
        for field in self.cfg["encrypted"]:
            credential[field] = self.gpg.decrypt(credential[field])
        return credential
