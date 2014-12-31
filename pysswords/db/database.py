import fnmatch
import os
import gnupg
import yaml

from pysswords.utils import which
from pysswords.crypt import create_keyring
from .credential import (
    CredentialExistsError,
    content,
    expandpath
)


class Database(object):

    def __init__(self, path):
        self.path = path

    @classmethod
    def create(cls, path, passphrase):
        os.makedirs(path)
        create_keyring(path, passphrase)
        return Database(path)

    @property
    def gpg(self):
        return gnupg.GPG(binary=which("gpg"),
                         homedir=self.keys_path)

    @property
    def keys_path(self):
        return os.path.join(self.path, ".keys")

    @property
    def credentials(self):
        creds = []
        for root, dirnames, filenames in os.walk(self.path):
            for filename in fnmatch.filter(filenames, '*.pyssword'):
                with open(os.path.join(root, filename)) as f:
                    creds.append(yaml.load(f))
        return creds

    def add(self, credential):
        cred_path = expandpath(self.path, credential)
        if os.path.isfile(cred_path):
            raise CredentialExistsError()
        os.makedirs(os.path.dirname(cred_path))
        with open(cred_path, "w") as f:
            f.write(content(credential))
        return cred_path
