import os
import argparse
import gnupg


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


def main():
    args = parse_args()
    gnupg.GPG(homedir=args.database)


if __name__ == "__main__":
    main()
