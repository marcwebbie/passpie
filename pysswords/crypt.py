import os
from shutil import which
import gnupg


def get_gpg(database_path):
    gnupg_path = os.path.join(database_path, ".gnupg")
    return gnupg.GPG(which("gpg2"), homedir=gnupg_path)
