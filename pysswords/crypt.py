from shutil import which
import gnupg


def get_gpg(gnupg_path):
    gnupg.GPG(which("gpg2"), homedir=gnupg_path)
