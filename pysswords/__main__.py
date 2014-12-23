from __future__ import print_function
import argparse
from getpass import getpass
import logging
import os

import colorama
import pyperclip
from tabulate import tabulate

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

colorama.init(autoreset=True)


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
    parser.add_argument("-e", "--edit", metavar="<CREDENTIAL NAME>",
                        help="edit credential")
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
    headers = ["name", "login", "password", "comments"]
    table = []
    for credential in database.credentials:
        row = [
            colorama.Fore.GREEN + credential.name + colorama.Fore.RESET,
            credential.login,
            "..." if not show_password else database.gpg.decrypt(
                credential.password,
                passphrase=passphrase
            ),
            credential.comments
        ]
        table.append(row)
    print(tabulate(table, headers, tablefmt="orgtbl"))


def prompt_credential(**defaults):
    credential_name = input("Name: ")
    credential_login = input("Login: ")
    credential_password = get_password("Credential password: ")
    credential_comments = input("Comments [optional]: ")
    return Credential(
        name=credential_name,
        login=credential_login,
        password=credential_password,
        comments=credential_comments,
    )


def add_credential(database):
    credential = prompt_credential()
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


def get_confirmation(prompt):
    prompt = "{} (y|n): ".format(prompt)
    return input(prompt)


def remove_credential(database, name):
    credential = database.credential(name=name)
    prompt = "Remove `{}`".format(credential)
    answer = get_confirmation(prompt)
    if answer and answer.lower()[0] == "y":
        database.remove(name=name)


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


def edit_credential(database, name):
    credential = database.credential(name=name)
    prompt = "Edit `{}`".format(credential)
    answer = get_confirmation(prompt)
    if answer and answer.lower()[0] == "y":
        edited_credential = prompt_credential()
        values = {
            "name": edited_credential.name,
            "login": edited_credential.login,
            "password": edited_credential.password,
            "comments": edited_credential.comments,
        }
        database.edit(name=name, values=values)


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
        elif args.edit:
            edit_credential(database, name=args.edit)
        elif args.search:
            list_credentials(database=database,
                             query=args.search,
                             show_password=args.show_password)
        else:
            list_credentials(database=database,
                             show_password=args.show_password)


if __name__ == "__main__":
    run()
