from getpass import getpass
import shutil
import logging
import colorama
import pyperclip
from tabulate import tabulate

from .python_two import is_python2, input
from .db.credential import splitname, asfullname
from .db import(
    Database,
    Credential
)


class CLI(object):

    def __init__(self, database_path, show_password, init=False):
        if init:
            self.create_database(path=database_path)
        self.database = Database(database_path)
        self.headers = ["Name", "Login", "Password", "Comment"]
        self.tablefmt = "orgtbl"
        self.show_password = show_password

    @classmethod
    def colored(cls, text, color):
        colorama_color = getattr(colorama.Fore, color.upper())
        return colorama_color + text + colorama.Fore.RESET

    @classmethod
    def create_database(cls, path):
        passphrase = CLI.prompt("Passphrase for database: ", password=True)
        database = Database.create(path, passphrase)
        cls.write("Database initialized in '{}'".format(path))
        return database

    @classmethod
    def write(cls, text):
        print(text)

    @classmethod
    def prompt_password(cls, text):
        for n in [1, 2, 3]:
            password = getpass(text)
            repeat_password = getpass("Type again: ")
            if password == repeat_password:
                return password
            elif n == 3:
                raise ValueError("Passwords didn't match.")
            else:
                cls.write("Entries don't match, try again.")

    @classmethod
    def prompt(cls, text, password=False):
        return cls.prompt_password(text) if password else input(text)

    @classmethod
    def prompt_credential(cls):
        credential_dict = {
            "name": cls.prompt("Name: "),
            "login": cls.prompt("Login: "),
            "password": cls.prompt("Password: ", password=True),
            "comment": cls.prompt("Comment: ")
        }
        return credential_dict

    @classmethod
    def prompt_confirmation(cls, text):
        entry = cls.prompt("{} (y|n): ".format(text))
        if entry and entry.lower().startswith("y"):
            return True
        else:
            return False

    def get_passphrase(self):
        passphrase = getpass("Passphrase: ")
        if self.database.check(passphrase):
            return passphrase
        else:
            raise ValueError("Wrong passphrase")

    def decrypt_credentials(self, credentials, passphrase):
        plaintext_credentials = []
        for c in credentials:
            new_credential = Credential(
                c.name,
                c.login,
                self.database.decrypt(c.password, passphrase),
                c.comment
            )

            plaintext_credentials.append(new_credential)
        return plaintext_credentials

    def build_table(self, credentials, color):
        table = []
        for credential in credentials:
            row = [
                CLI.colored(credential.name, color),
                credential.login,
                credential.password if self.show_password else "***",
                credential.comment
            ]
            table.append(row)
        return tabulate(table, self.headers, tablefmt=self.tablefmt)

    def show(self, credentials=None, color="yellow"):
        if not credentials:
            credentials = self.database.credentials

        if len(credentials) > 0:
            if self.show_password:
                credentials = self.decrypt_credentials(
                    credentials,
                    passphrase=self.get_passphrase())
            table = self.build_table(credentials, color)
            self.write("\n{}\n".format(table))

    def add_credential(self):
        credential = self.prompt_credential()
        fullname = asfullname(credential["name"], credential["login"])
        self.database.add(**credential)
        logging.info("Added credential '{}'".format(fullname))

    def get_credentials(self, fullname):
        name, login = splitname(fullname)
        self.show(self.database.get(name=name, login=login))

    def search_credentials(self, query):
        self.show(self.database.search(query=query))

    def remove_credentials(self, fullname):
        name, login = splitname(fullname)
        credentials = self.database.get(name=name, login=login)
        self.show(credentials, color="Red")
        confirmed = self.prompt_confirmation("Remove these credentials?")
        if confirmed:
            self.database.remove(name=name, login=login)
            for cred in credentials:
                logging.info("Removed {}".format(
                    asfullname(cred.name, cred.login)))

    def update_credentials(self, fullname):
        name, login = splitname(fullname)
        self.show(self.database.get(name=name, login=login), color="Red")
        confirmed = self.prompt_confirmation("Edit these credentials?")
        if confirmed:
            values = self.prompt_credential()
            clean_values = {k: v for k, v in values.items() if v}
            updated_credentials = self.database.update(
                name=name,
                login=login,
                to_update=clean_values)
            for cred in updated_credentials:
                logging.info("Updated credential: {}".format(
                    asfullname(cred.name, cred.login)))

    def copy_to_clipboard(self, fullname):
        name, login = splitname(fullname)
        credentials = self.database.get(name=name, login=login)

        if len(credentials) > 1:
            logging.warning("Multiple credentials were found."
                            "Copying first credential password to clipboard")

        credential = credentials[0]
        passphrase = self.get_passphrase()
        pyperclip.copy(
            self.database.decrypt(credential.password, passphrase))
        logging.info("Password for `{}` copied to clipboard".format(
            asfullname(credential.name, credential.login)))

    def exportdb(self, dbfile):
        self.database.exportdb(dbfile)

    def importdb(self, dbfile):
        self.database.importdb(dbfile)

    def clean_database(self):
        confirmed = self.prompt_confirmation(
            "Delete database at '{}'? ".format(self.database.path))
        if confirmed:
            shutil.rmtree(self.database.path)
            logging.info("Database '{}' deleted.".format(self.database.path))
