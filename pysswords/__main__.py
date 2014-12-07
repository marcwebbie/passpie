import argparse
from getpass import getpass
from pysswords.db import Database
from pysswords.crypt import CryptOptions


def get_args():
    parser = argparse.ArgumentParser()
    main_group = parser.add_argument_group('Main options')
    main_group.add_argument('path', help='Path to database file')
    main_group.add_argument('--create', action='store_true',
                            help='Create a new encrypted password database')

    crypt_group = parser.add_argument_group('Encryption options')
    crypt_group.add_argument('--password', default=None,
                             help='Password to open database')
    crypt_group.add_argument('--salt', default=None,
                             help='Salt for encryption')
    crypt_group.add_argument('--iterations', default=100000,
                             help='Number of iterations for encryption')

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
