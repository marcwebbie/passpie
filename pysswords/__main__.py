from __future__ import unicode_literals
import argparse
import logging
import os
from pkg_resources import get_distribution

from .cli import CLI
from .db import (
    CredentialExistsError,
    CredentialNotFoundError,
    DatabaseExistsError
)
from .utils import which


__project__ = 'pysswords'
__version__ = get_distribution('pysswords').version


def default_db():
    return os.path.join(os.path.expanduser("~"), ".pysswords")


def parse_args(cli_args=None):
    parser = argparse.ArgumentParser(prog="Pysswords")

    group_db = parser.add_argument_group("Database options")
    group_db.add_argument("-I", "--init", action="store_true",
                          help="create a new Pysswords database")
    group_db.add_argument("-D", "--database", default=default_db(),
                          help="specify path to database")
    group_db.add_argument("--export", dest="exportdb", metavar="DATABASE_FILE",
                          help="export encrypted Pysswords database")
    group_db.add_argument("--import", dest="importdb", metavar="DATABASE_FILE",
                          help="import encrypted Pysswords database")
    group_db.add_argument("--clean", action="store_true",
                          help="delete database, cleaning all files")

    group_cred = parser.add_argument_group("Credential options")
    group_cred.add_argument("-a", "--add", action="store_true",
                            help="add new credential")
    group_cred.add_argument("-g", "--get", metavar="FULLNAME",
                            help="get credentials by name")
    group_cred.add_argument("-u", "--update", metavar="FULLNAME",
                            help="update credentials")
    group_cred.add_argument("-r", "--remove", metavar="FULLNAME",
                            help="remove credentials")
    group_cred.add_argument("-c", "--clipboard", metavar="FULLNAME",
                            help="copy credential password to clipboard")
    group_cred.add_argument("-s", "--search",
                            help="search credentials. [regex supported]")
    group_cred.add_argument("-P", "--show-password", action="store_true",
                            help="show credentials passwords as plain text")

    group_runtime = parser.add_argument_group("Default options")
    group_runtime.add_argument("--version", action="version",
                               version="Pysswords {}".format(__version__),
                               help="Print version")
    group_runtime.add_argument("--verbose", "-v", action="store_true",
                               help="Print verbose output")

    args = parser.parse_args(cli_args)
    return args


def main(cli_args=None):

    if not which("gpg"):
        logging.error("GPG not installed: https://gnupg.org/download")
        exit(1)

    args = parse_args(cli_args)

    if args.verbose:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    try:
        interface = CLI(
            database_path=args.database,
            show_password=args.show_password,
            init=args.init
        )

        if args.exportdb:
            interface.exportdb(args.exportdb)
        elif args.importdb:
            interface.importdb(args.importdb)
        elif args.clean:
            interface.clean_database()
        elif args.add:
            interface.add_credential()
        elif args.clipboard:
            interface.copy_to_clipboard(fullname=args.clipboard)
        elif args.get:
            interface.get_credentials(fullname=args.get)
        elif args.search:
            interface.search_credentials(query=args.search)
        elif args.update:
            interface.update_credentials(fullname=args.update)
        elif args.remove:
            interface.remove_credentials(fullname=args.remove)
        else:
            interface.show()
    except CredentialExistsError as e:
        logging.error("Credential '{}' exists".format(e))
    except CredentialNotFoundError as e:
        logging.error("Credential '{}' not found".format(e))
    except DatabaseExistsError as e:
        logging.error(str(e))
    except ValueError as e:
        logging.error(str(e))
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt")

if __name__ == "__main__":
    main()
