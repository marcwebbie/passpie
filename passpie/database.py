from functools import partial
import os

from tinydb import TinyDB, Storage
import yaml
from .utils import mkdir_open


class PasspieStorage(Storage):
    extension = ".pass"

    def __init__(self, path):
        super(PasspieStorage, self).__init__()
        self.path = path

    def read(self):
        elements = []
        for rootdir, dirs, files in os.walk(self.path):
            filenames = [f for f in files if f.endswith(self.extension)]
            for filename in filenames:
                docpath = os.path.join(rootdir, filename)
                with open(docpath) as f:
                    elements.append(yaml.load(f.read()))

        data = {}
        for idx, elem in enumerate(elements, start=1):
            data[idx] = elem
        return {"_default": data}

    def write(self, data):
        for id, cred in data["_default"].items():
            dirname, filename = cred["name"], cred["login"] + self.extension
            credpath = os.path.join(self.path, dirname, filename)
            with mkdir_open(credpath, "w") as f:
                f.write(yaml.dump(cred, default_flow_style=False))


Database = partial(TinyDB, storage=PasspieStorage)
