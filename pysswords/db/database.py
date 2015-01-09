import fnmatch
import os
import shutil
import yaml

from pysswords.crypt import create_keyring, getgpg
from .credential import (
    Credential,
    CredentialExistsError,
    content,
    expandpath
)

from pysswords.python_two import makedirs


class Database(object):

    def __init__(self, path):
        self.path = path
        self.keys_path = os.path.join(self.path, ".keys")
        self.gpg = getgpg(self.keys_path)

    @classmethod
    def create(cls, path, passphrase):
        os.makedirs(path)
        create_keyring(os.path.join(path, ".keys"), passphrase)
        return Database(path)

    @property
    def credentials(self):
        creds = []
        for root, dirnames, filenames in os.walk(self.path):
            for filename in fnmatch.filter(filenames, '*.pyssword'):
                with open(os.path.join(root, filename)) as f:
                    creds.append(yaml.load(f))
        return creds

    def key(self, private=False):
        key = next(k for k in self.gpg.list_keys(secret=private))
        return key.get("fingerprint")

    def remove(self, credential):
        credential_path = expandpath(self.path, credential)
        credential_dir = os.path.dirname(credential_path)
        os.remove(credential_path)
        if not os.listdir(credential_dir):
            shutil.rmtree(credential_dir)

    def add(self, credential):
        cred_path = expandpath(self.path, credential)
        if os.path.isfile(cred_path):
            raise CredentialExistsError()
        makedirs(os.path.dirname(cred_path), exist_ok=True)
        with open(cred_path, "w") as f:
            f.write(content(credential))
        return cred_path

    def update(self, credential, **values):
        name = values.get("name", credential.name)
        login = values.get("login", credential.login)
        password = values.get("password", credential.password)
        comment = values.get("comment", credential.comment)
        self.remove(credential)
        new_credential = Credential(name, login, password, comment)
        self.add(new_credential)
        return new_credential

    def credential(self, name, login=None):
        if login:
            return [c for c in self.credentials
                    if c.name == name and c.login == login]
        else:
            return [c for c in self.credentials if c.name == name]

    def search(self, query):
        return [cred for cred in self.credentials
                if query in " ".join([v for v in cred])]

    def encrypt(self, text):
        encrypted = self.gpg.encrypt(
            text,
            self.key(),
            cipher_algo="AES256")
        return str(encrypted)

    def decrypt(self, text, passphrase):
        decrypted = str(self.gpg.decrypt(text, passphrase=passphrase))
        return decrypted

    def check(self, passphrase):
        sign = self.gpg.sign(
            "testing",
            default_key=self.key(True),
            passphrase=passphrase
        )
        return True if sign else False
