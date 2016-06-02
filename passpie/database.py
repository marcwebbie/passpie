from copy import deepcopy
from datetime import datetime
import os
import re
import shutil
import yaml

from tinydb import TinyDB, Storage, Query
from tinydb.database import Table
from tinydb.middlewares import Middleware

from .utils import is_repo_url, mkdir_open
from .history import clone, Repository


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


class CredentialStorage(Storage):
    extension = ".pass"

    def __init__(self, path, extension):
        self.path = os.path.expanduser(path)
        self.extension = extension

    def make_path(self, element):
        return os.path.join(self.path,
                            element['name'],
                            element['login'] + self.extension)

    def read(self):
        elements = []
        for rootdir, dirs, files in os.walk(self.path):
            for fpath in [f for f in files if f.endswith(self.extension)]:
                with open(os.path.join(rootdir, fpath)) as f:
                    credential = yaml.load(f.read())
                credential['name'] = os.path.relpath(rootdir, self.path)
                login, extension = os.path.splitext(fpath)
                if not extension:
                    login = ''
                credential['login'] = login
                credential['fullname'] = make_fullname(
                    login=credential['login'], name=credential['name'])
                elements.append(credential)
        return {"_default": {i: e for i, e in enumerate(elements)}}

    def write(self, data):
        elements = data['_default'].values()
        for element in [e for e in elements if e.get('_deleted')]:
            self.delete_credential(element)
        for element in [e for e in elements if e.get('_updated')]:
            element = deepcopy(element)
            self.delete_credential(element)
            element.update(element["_updated"])
            self.write_credential(element)
        for element in [e for e in elements if e.get('_created')]:
            self.write_credential(element)

    def delete_credential(self, element):
        filepath = self.make_path(element)
        dirpath = os.path.dirname(filepath)
        os.remove(filepath)
        if not os.listdir(dirpath):
            shutil.rmtree(os.path.dirname(filepath))

    def write_credential(self, element):
        filepath = self.make_path(element)
        element['modified'] = datetime.now()
        with mkdir_open(filepath, "w") as f:
            element.pop("name", None)
            element.pop("login", None)
            element.pop("_created", None)
            element.pop("_deleted", None)
            element.pop("_updated", None)
            f.write(yaml.dump(element, default_flow_style=False))


class CredentialTable(Table):

    private_fields = ["password"]

    def cond(self, fullname):
        Credential = Query()
        login, name = split_fullname(fullname)
        if login:
            return (Credential.name == name) & (Credential.login == login)
        else:
            return (Credential.name == name)

    def insert(self, element):
        element['_created'] = True
        element['modified'] = datetime.now()
        return super(CredentialTable, self).insert(element)

    def update(self, fields, fullname):
        def _update(data, eid):
            fields["modified"] = datetime.now()
            data[eid]['_updated'] = fields
        return self.process_elements(_update, self.cond(fullname))

    def remove(self, fullname):
        def _remove(data, eid):
            data[eid]['_deleted'] = True
        return self.process_elements(_remove, self.cond(fullname))

    def credential(self, fullname):
        Credential = Query()
        login, name = split_fullname(fullname)
        if login:
            return self.get((Credential.name == name) & (Credential.login == login))
        else:
            return self.get((Credential.name == name))

    def all(self, decryptor=None):
        if decryptor:
            data = []
            for elem in super(CredentialTable, self).all():
                for key in elem.keys():
                    if key in self.private_fields:
                        elem[key] = decryptor(elem[key])
                data.append(elem)
            return data
        else:
            return super(CredentialTable, self).all()

    def matches(self, regex):
        Credential = Query()
        return self.search(
            Credential.name.matches(regex) |
            Credential.login.matches(regex) |
            Credential.comment.matches(regex)
        )

    def purge(self):
        self.process_elements(self._remove, cond=all)

    def _remove(self, data, eid):
        data[eid]['_deleted'] = True


class Database(TinyDB):

    def __init__(self, path, autopush=None, autopull=None, extension='.pass'):
        self.path = path
        if is_repo_url(self.path):
            self.path = clone(self.path)
        self.repo = Repository(self.path, autopull=autopull, autopush=autopush)

        self.table_class = CredentialTable
        super(Database, self).__init__(
            self.path,
            extension=extension,
            storage=CredentialStorage
        )
