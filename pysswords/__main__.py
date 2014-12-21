from __future__ import print_function
import argparse
from getpass import getpass
import logging
import os

from .db import Database
from .credential import Credential


DEFAULT_DATABASE_PATH = os.path.join(
    os.path.expanduser("~"),
    ".pysswords"
)

DEFAULT_GPG_BINARY = "gpg2"


def get_args(command_args=None):
    """Return args from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("-d", "--database", default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--gpg", default=DEFAULT_GPG_BINARY)
    parser.add_argument("task", choices=['init', 'add', 'search'])
    args = parser.parse_args(command_args)
    return args


def get_passphrase():
    for _ in range(3):
        passphrase = getpass("Database passphrase: ")
        repeat_passphrase = getpass("Type passphrase again: ")

        if passphrase == repeat_passphrase:
            return passphrase
        else:
            print("Passphrases don't match!")
    else:
        raise ValueError("Passwords didn't match")


def run(args=None):
    args = get_args() if args is None else args

    if args.task == "init":
        database = Database.create(
            path=args.database,
            passphrase=get_passphrase(),
            gpg_bin=args.gpg
        )
        logging.info("Database created at '{}'".format(database.path))
    elif args.task == "add":
        credential_name = input("Name: ")
        credential_login = input("Login: ")
        credential_password = input("Password: ")
        credential_comments = input("Comments [optional]: ")
        credential = Credential(
            name=credential_name,
            login=credential_login,
            password=credential_password,
            comments=credential_comments,
        )
        database = Database.from_path(
            path=args.database,
            gpg_bin=args.gpg
        )
        database.add(credential)


if __name__ == "__main__":
    run()
