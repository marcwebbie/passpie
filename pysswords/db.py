from . import crypt


def init(database_path):
    gpg = crypt.get_gpg(database_path)
