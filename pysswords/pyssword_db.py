# support python2
try:
    input = raw_input
except NameError:
    pass
try:
    from collections import namedtuple
except ImportError:
    from namedtuple import namedtuple

from pyscrypt import ScryptFile
from pyscrypt.file import InvalidScryptFileFormat


Credential = namedtuple(
    "Credential",
    ["name", "login", "password", "login_url", "description"]
)


class PysswordDB(object):
    """Passwords database"""

    def __init__(self, db_path, password, verbose=False):
        self._file_path = db_path
        self.password = password
        self.credentials = []

        with open(db_path, "w") as db_file:
            scrypt_file = ScryptFile(db_file, self.password, N=1024, r=1, p=1)
            scrypt_file.close()

            if verbose:
                print("Pysswords database created: '{}'".format(db_path))

    @property
    def valid(self):
        with open(self._file_path) as db_file:
            try:
                ScryptFile.verify_file(db_file, self.password)
                return True
            except: # TODO: Patch pyscrypt for raising specific exception
                return False

    @property
    def count(self):
        """Count the number of credentials registered"""
        return len(self.credentials)

    def add_credential(self, credential):
        """Add new credential to database"""
        self.credentials.append(credential)

    def get_credential(self, name):
        """Get credential"""
        for credential in self.credentials:
            if credential.name == name:
                return credential
        else:
            return None
