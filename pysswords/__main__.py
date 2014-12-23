from __future__ import print_function
import argparse
from getpass import getpass
import logging
import os

import pyperclip

from .db import Database
from .credential import Credential, CredentialNotFoundError

try:
    input = raw_input
except NameError:
    pass

DEFAULT_DATABASE_PATH = os.path.join(
    os.path.expanduser("~"),
    ".pysswords"
)

DEFAULT_GPG_BINARY = "gpg"


def get_args(command_args=None):
    """Return args from command line"""
    parser = argparse.ArgumentParser(prog="pysswords")
    parser.add_argument("-I", "--init", action="store_true",
                        help="create a new Pysswords database")
    parser.add_argument("-d", "--database", default=DEFAULT_DATABASE_PATH,
                        metavar="<DATABASE PATH>",
                        help="specify path to database")
    parser.add_argument("--show-password", action="store_true",
                        help="show password as plain text when print")
    parser.add_argument("-a", "--add", action="store_true",
                        help="add new credential")
    parser.add_argument("-r", "--remove", metavar="<CREDENTIAL NAME>",
                        help="delete credential")
    parser.add_argument("-s", "--search", metavar="<QUERY>",
                        help="search credential")
    parser.add_argument("-g", "--get", metavar="<CREDENTIAL NAME>",
                        help="print credential")
    parser.add_argument("-l", "--list", action="store_true",
                        help="print all credentials as a table")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="copy credential password to clipboard")
    parser.add_argument("--gpg", metavar="<GPG>", default=DEFAULT_GPG_BINARY,
                        help="gpg binary name")
    args = parser.parse_args(command_args)

    if args.clipboard and not args.get:
        parser.error('-g argument is required in when using -c')
    return args


def get_password(prompt="Password: "):
    for _ in range(3):
        password = getpass(prompt)
        repeat_password = getpass("Type again: ")

        if password == repeat_password:
            return password
        else:
            print("Entries don't match!")
    else:
        raise ValueError("Entries didn't match")


def check_passphrase(database, passphrase):
    sig = database.gpg.sign(
        'testing',
        default_key=database.gpg_key,
        passphrase=passphrase
    )
    if not sig:
        msg = "Wrong passphrase for database at '{}'".format(database.path)
        raise ValueError(msg)
    return sig


def list_credentials(database, query=None, show_password=False):
    if show_password:
        passphrase = getpass("Database passphrase: ")
        check_passphrase(database, passphrase)
    credentials = database.search(query) if query else database.credentials
    for idx, credential in enumerate(credentials):
        cred_string = "[{0}] {1}: login={2}, password={3}, {4}".format(
            idx,
            credential.name,
            credential.login,
            "..." if not show_password else database.gpg.decrypt(
                credential.password,
                passphrase=passphrase
            ),
            credential.comments
        )
        print(cred_string)


def add_credential(database):
    credential_name = input("Name: ")
    credential_login = input("Login: ")
    credential_password = getpass("Credential password: ")
    credential_comments = input("Comments [optional]: ")
    credential = Credential(
        name=credential_name,
        login=credential_login,
        password=credential_password,
        comments=credential_comments,
    )
    database.add(credential)


def copy_password_to_clipboard(database, credential_name):
    credential = database.credential(name=credential_name)
    if credential:
        passphrase = getpass("Database passphrase: ")
        check_passphrase(database, passphrase)
        pyperclip.copy(
            database.gpg.decrypt(credential.password, passphrase=passphrase)
        )
        print("Password for '{}' copied to clipboard".format(credential.name))


def remove_credential(database, name):
    credential = database.credential(name=name)
    try:
        prompt = "Delete credential `{}` (y|n): ".format(credential)
        answer = input(prompt)
    except KeyboardInterrupt:
        print("")
    if answer and answer.lower()[0] == "y":
        database.delete(name=name)


def get_credential(database, name, to_clipboard=False):
    try:
        credential = database.credential(name=name)
        if to_clipboard:
            copy_password_to_clipboard(database=database,
                                       credential_name=name)
        else:
            print(credential)
    except CredentialNotFoundError:
        logging.info("Credential was not found")


def run(args=None):
    args = get_args() if args is None else args

    if args.init:
        database = Database.create(
            path=args.database,
            passphrase=get_password("Database passphrase: "),
            gpg_bin=args.gpg
        )
        logging.info("Database created at '{}'".format(database.path))
    else:
        database = Database.from_path(path=args.database,
                                      gpg_bin=args.gpg)
        if args.add:
            add_credential(database)
        elif args.get:
            get_credential(database,
                           name=args.get,
                           to_clipboard=args.clipboard)
        elif args.remove:
            remove_credential(database, name=args.remove)
        elif args.search:
            list_credentials(database=database,
                             query=args.search,
                             show_password=args.show_password)
        else:
            list_credentials(database=database,
                             show_password=args.show_password)


if __name__ == "__main__":
    run()
