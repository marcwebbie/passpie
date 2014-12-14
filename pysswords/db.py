from glob import glob
import os

from . import crypt


def init(database_path):
    gpg = crypt.get_gpg(database_path)


def get_credential(credential_path):
    login_file_path = os.path.join(credential_path, "login")
    password_file_path = os.path.join(credential_path, "password")
    comments_file_path = os.path.join(credential_path, "comments")
    credential = {
        'name': os.path.basename(credential_path),
        'login': open(login_file_path).read(),
        'password': open(password_file_path).read(),
        'comments': open(comments_file_path).read()
    }
    return credential


def list_credentials(database_path):
    return [get_credential(c) for c in glob(database_path + "/**")]
