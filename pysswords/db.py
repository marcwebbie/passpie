import os


def init(database_path):
    gnupg_path = os.path.join(database_path, ".gnupg")
    os.makedirs(gnupg_path)
