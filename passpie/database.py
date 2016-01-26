from datetime import datetime
import logging
import os
import re
import shutil

from tinydb import TinyDB, Storage, where, Query
import yaml

from .utils import mkdir_open
from .history import Repository
from .credential import split_fullname, make_fullname


def is_repo_url(path):
    if path:
        return re.match(
            r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?',
            path
        )


class PasspieStorage(Storage):
    extension = ".pass"

    def __init__(self, path):
        super(PasspieStorage, self).__init__()
        self.path = path

    def delete(self, credentials):
        for cred in credentials:
            dirname, filename = cred["name"], cred["login"] + self.extension
            credpath = os.path.join(self.path, dirname, filename)
            os.remove(credpath)
            if not os.listdir(os.path.dirname(credpath)):
                shutil.rmtree(os.path.dirname(credpath))

    def read(self):
        elements = []
        for rootdir, dirs, files in os.walk(self.path):
            filenames = [f for f in files if f.endswith(self.extension)]
            for filename in filenames:
                docpath = os.path.join(rootdir, filename)
                with open(docpath) as f:
                    elements.append(yaml.load(f.read()))

        return {"_default":
                {idx: elem for idx, elem in enumerate(elements, start=1)}}

    def write(self, data):
        deleted = [c for c in self.read()["_default"].values()
                   if c not in data["_default"].values()]
        self.delete(deleted)

        for eid, cred in data["_default"].items():
            dirname, filename = cred["name"], cred["login"] + self.extension
            credpath = os.path.join(self.path, dirname, filename)
            with mkdir_open(credpath, "w") as f:
                f.write(yaml.dump(dict(cred), default_flow_style=False))


class Database(TinyDB):

    def __init__(self, config, storage=PasspieStorage):
        self.config = config
        self.path = config['path']
        self.repo = Repository(self.path,
                               autopull=config.get('autopull'),
                               autopush=config.get('autopush'))
        PasspieStorage.extension = config['extension']
        super(Database, self).__init__(self.path, storage=storage)

    def has_keys(self):
        return os.path.exists(os.path.join(self.path, '.keys'))

    def credential(self, fullname):
        login, name = split_fullname(fullname)
        return self.get((where("login") == login) & (where("name") == name))

    def add(self, fullname, password, comment):
        login, name = split_fullname(fullname)
        if login is None:
            logging.error('Cannot add credential with empty login. use "@<name>" syntax')
            return None
        credential = dict(fullname=fullname,
                          name=name,
                          login=login,
                          password=password,
                          comment=comment,
                          modified=datetime.now())
        self.insert(credential)
        return credential

    def update(self, fullname, values):
        values['fullname'] = make_fullname(values["login"], values["name"])
        values['modified'] = datetime.now()
        self.table().update(values, (where("fullname") == fullname))

    def credentials(self, fullname=None):
        if fullname:
            login, name = split_fullname(fullname)
            Credential = Query()
            if login is None:
                creds = self.search(Credential.name == name)
            else:
                creds = self.search((Credential.login == login) & (Credential.name == name))
        else:
            creds = self.all()
        return sorted(creds, key=lambda x: x["name"] + x["login"])

    def remove(self, fullname):
        self.table().remove(where('fullname') == fullname)

    def matches(self, regex):
        Credential = Query()
        credentials = self.search(
            Credential.name.matches(regex) |
            Credential.login.matches(regex) |
            Credential.comment.matches(regex)
        )
        return sorted(credentials, key=lambda x: x["name"] + x["login"])
