import argparse
from getpass import getpass
import os
import re

from .db import Database, Credential


def default_db():
    return os.path.join(os.path.expanduser("~"), ".pysswords")


def parse_args(cli_args=None):
    parser = argparse.ArgumentParser(prog="Pysswords")

    group_db = parser.add_argument_group("Databse options")
    group_db.add_argument("-I", "--init", action="store_true")
    group_db.add_argument("-D", "--database", default=default_db())

    group_cred = parser.add_argument_group("Credential options")
    group_cred.add_argument("-a", "--add", action="store_true")
    group_cred.add_argument("-g", "--get")
    group_cred.add_argument("-u", "--update")
    group_cred.add_argument("-r", "--remove")
    group_cred.add_argument("-s", "--search")
    group_cred.add_argument("-c", "--clipboard", action="store_true")

    args = parser.parse_args(cli_args)
    if args.clipboard and not args.get:
        parser.error('-g argument is required in when using -c')

    return args


def prompt_password(text):
    for _ in range(3):
        password = getpass(text)
        repeat_password = getpass("Type again: ")

        if password == repeat_password:
            return password
        else:
            print("Entries don't match!")
    else:
        raise ValueError("Entries didn't match")


def prompt(text, default="", password=False):
    if password:
        prompt_password(text)
    else:
        entry = input("{} {}: ".format(text, "[{}]".format(default)))
        return entry


def prompt_credential(database, **defaults):
    name = prompt("Name", defaults.get("name"))
    login = prompt("Login", defaults.get("login"))
    password = prompt("Password")
    comment = prompt("Comment", defaults.get("comment"))
    return Credential(name, login, database.encrypt(password), comment)


def split_name(fullname):
    rgx = re.compile(r"(?:(?P<login>.+)?@)?(?P<name>[\w\s\._-]+)")
    if rgx.match(fullname):
        name = rgx.match(fullname).group("name")
        login = rgx.match(fullname).group("login")
        return name, login
    else:
        raise ValueError("Not a valid name")


def main(cli_args):
    args = parse_args(cli_args)
    if args.init:
        passphrase = prompt("Passhprase for database", password=True)
        database = Database.create(args.database, passphrase)
    else:
        database = Database(path=args.database)

    if args.add:
        credential = prompt_credential(database)
        database.add(credential)

    if args.get:
        name, login = split_name(args.get)
        database.credential(name=name, login=login)


if __name__ == "__main__":
    main()
