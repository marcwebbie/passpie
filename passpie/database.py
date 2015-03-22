from functools import partial
import os
import shutil

from tinydb import TinyDB, Storage
import yaml
from .utils import mkdir_open


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


Database = partial(TinyDB, storage=PasspieStorage)
