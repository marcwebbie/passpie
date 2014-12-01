from pyscrypt import ScryptFile
from pyscrypt.file import InvalidScryptFileFormat

# support python2
try:
    input = raw_input
except NameError:
    pass


class PysswordDB(object):
    """Passwords database"""

    def __init__(self, db_path, password, verbose=False):
        self._file_path = db_path

        with open(db_path, "w") as db_file:
            scrypt_file = ScryptFile(db_file, password, N=1024, r=1, p=1)
            scrypt_file.close()

            if verbose:
                print("Pysswords database created: '{}'".format(db_path))

    def is_valid(self, password):
        with open(self._file_path) as db_file:
            if ScryptFile.verify_file(db_file, password):
                return True
            else:
                return False
