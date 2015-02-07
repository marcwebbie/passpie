import fnmatch
import os
import re
import shutil
import tarfile
import yaml

from pysswords.crypt import create_keyring, getgpg, is_encrypted
from .credential import (
    Credential,
    CredentialNotFoundError,
    CredentialExistsError,
    content,
    expandpath,
    exists,
    clean,
    asstring,
    asfullname
)

from pysswords.python_two import makedirs


class DatabaseExistsError(Exception):
    pass


class Database(object):

    def __init__(self, path):
        self.path = path
        self.keys_path = os.path.join(self.path, ".keys")
        self.gpg = getgpg(self.keys_path)

    @classmethod
    def create(cls, path, passphrase):
        try:
            makedirs(path, exist_ok=False)
        except OSError:
            raise DatabaseExistsError("Database exists")
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
        try:
            key = next(k for k in self.gpg.list_keys(secret=private))
        except StopIteration:
            raise ValueError("Database key not found or corrupted")
        return key.get("fingerprint")

    def build_credential(self, name, login, password, comment, encrypt=True):
        if encrypt and not is_encrypted(password):
            password = self.encrypt(password)
        return Credential(
            name=name,
            login=login,
            password=password,
            comment=comment
        )

    def write_credential(self, credential):
        if exists(self.path, credential.name, credential.login):
            raise CredentialExistsError(
                asfullname(credential.name, credential.login))
        cred_path = expandpath(self.path, credential.name, credential.login)
        makedirs(os.path.dirname(cred_path), exist_ok=True)
        with open(cred_path, "w") as f:
            f.write(content(credential))
        return cred_path

    def add(self, name, login, password, comment):
        credential = self.build_credential(name, login, password, comment)
        self.write_credential(credential)
        return credential

    def update(self, name, login, to_update):
        found = self.get(name, login)
        updated = []
        for credential in found:
            new_credential = self.build_credential(
                name=to_update.get("name", credential.name),
                login=to_update.get("login", credential.login),
                password=to_update.get("password", credential.password),
                comment=to_update.get("comment", credential.comment),
                encrypt=True if to_update.get("password") else False
            )
            self.remove(credential.name, credential.login)
            self.add(
                name=new_credential.name,
                login=new_credential.login,
                password=new_credential.password,
                comment=new_credential.comment,
            )
            updated.append(new_credential)
        return updated

    def remove(self, name, login):
        found = self.get(name, login)
        for credential in found:
            clean(self.path, credential.name, credential.login)

    def get(self, name, login=None):
        found = [c for c in self.credentials
                 if c.name == name and ((login is None) or c.login == login)]
        if not found:
            raise CredentialNotFoundError(asfullname(name, login))
        else:
            return found

    def search(self, query):
        rgx = re.compile(query)
        return [c for c in self.credentials if rgx.search(asstring(c))]

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

    def exportdb(self, dbfile):
        os.rename(shutil.make_archive(dbfile, "tar", self.path), dbfile)

    def importdb(self, dbfile):
        with tarfile.open(dbfile) as tar:
            tar.extractall(self.path)
