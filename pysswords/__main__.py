import argparse
from getpass import getpass
from pysswords.db import Database, Credential
from pysswords.crypt import CryptOptions

try:
    # python2 support
    input = raw_input
except NameError:
    pass


def get_args():
    parser = argparse.ArgumentParser()
    main_group = parser.add_argument_group('Main options')
    main_group.add_argument('path', help='Path to database file')
    main_group.add_argument('--create', action='store_true',
                            help='Create a new encrypted password database')
    main_group.add_argument('--add', action='store_true',
                            help='Add new credential to password database')

    crypt_group = parser.add_argument_group('Encryption options')
    crypt_group.add_argument('--password', default=None,
                             help='Password to open database')
    crypt_group.add_argument('--salt', default=None,
                             help='Salt for encryption')
    crypt_group.add_argument('--iterations', default=100000,
                             help='Number of iterations for encryption')

    return parser.parse_args()


def get_credential():
    name = input("Name : ")
    login = input("Login : ")

    # Password
    passwords_match = False
    for i in range(3):
        password = getpass("Credential password : ")
        password_retype = getpass("Enter Credential password again: ")
        if password == password_retype:
            passwords_match = True
            break
        else:
            print("Passwords don't match. Try again")
    if not passwords_match:
        raise ValueError("Passwords for credential don't match")

    login_url = input("Login url [optional]: ")
    description = input("Description [optional] : ")

    credential = Credential(
        name=name,
        login=login,
        password=password,
        login_url=login_url,
        description=description
    )
    return credential


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
    else:
        if args.add:
            database = Database(args.path, crypt_options)
            credential = get_credential()
            database.add_credential(credential)


if __name__ == "__main__":
    main()
