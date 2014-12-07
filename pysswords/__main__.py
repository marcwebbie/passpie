import argparse
from getpass import getpass
from pysswords.db import Database
from pysswords.crypt import CryptOptions


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--password', action='store_true')

    parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    if not args.password:
        getpass()

    crypt_options = CryptOptions(
        password=args.password,
        salt=None,
        iterations=1000
    )

    if args.create:
        database_created = Database.create()


if __name__ == "__main__":
    main()
