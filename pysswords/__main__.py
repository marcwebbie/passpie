import argparse
from getpass import getpass
import os

from .db import Database


def get_args(command_args=None):
    """Return args from command line"""
    default_database_path = os.path.join(
        os.path.expanduser("~"),
        ".pysswords"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--database", default=default_database_path)
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

    if args.init:
        database = Database.create(
            path=args.database,
            passphrase=get_passphrase())


if __name__ == "__main__":
    run()
