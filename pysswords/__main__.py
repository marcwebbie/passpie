import argparse
from getpass import getpass
from pysswords.db import Database
from pysswords.crypt import CryptOptions


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--password', default=None)
    parser.add_argument('--salt', default=None)
    parser.add_argument('--iterations', default=100000)

    return parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    if not args.password:
        args.password = getpass()

    crypt_options = CryptOptions(
        password=args.password,
        salt=args.salt,
        iterations=args.iterations
    )

    if args.create:
        Database.create(args.path, crypt_options)
    elif args.add:
        database = Database(args.path, crypt_options)
        database.add_credential(args.path, crypt_options)


if __name__ == "__main__":
    main()
