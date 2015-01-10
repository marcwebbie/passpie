from getpass import getpass
import colorama
import pyperclip
from tabulate import tabulate

from .db import Database, Credential
from .db.credential import splitname, asfullname


class CLI(object):

    def __init__(self, database_path, show_password, init=False):
        if init:
            self.create_database(path=database_path)
        self.database = Database(database_path)
        self.headers = ["Name", "Login", "Password", "Comment"]
        self.tablefmt = "orgtbl"
        self.display = self.database.credentials
        self.show_password = show_password

    @classmethod
    def colored(cls, text, color):
        colorama_color = getattr(colorama.Fore, color.upper())
        return colorama_color + text + colorama.Fore.RESET

    @classmethod
    def create_database(cls, path):
        passphrase = CLI.prompt("Passphrase for database", password=True)
        database = Database.create(path, passphrase)
        return database

    @classmethod
    def prompt_password(cls, text):
        for _ in range(3):
            password = getpass(text)
            repeat_password = getpass("Type again: ")
            if password == repeat_password:
                return password
            else:
                print("Entries don't match!")
        else:
            raise ValueError("Entries didn't match")

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
        entry = input("{} (y|n): ".format(text))
        if entry and entry.lower().startswith("y"):
            return True
        else:
            return False

    def get_passphrase(self):
        passphrase = getpass("Passphrase: ")
        if self.database.check(passphrase):
            return passphrase


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

    def show_display(self):
        if self.show_password:
            passphrase = self.get_passphrase()
            if passphrase is not None:
                credentials = self.decrypt_credentials(
                    self.display,
                    passphrase
                )
            else:
                return self.write("Wrong passphrase", error=True)
        else:
            credentials = self.display

        table = []
        for credential in credentials:
            row = [
                CLI.colored(credential.name, "yellow"),
                credential.login,
                credential.password if self.show_password else "***",
                credential.comment
            ]
            table.append(row)
        print("")
        print(tabulate(table, self.headers, tablefmt=self.tablefmt))
        print("")

    def add_credential(self):
        credential = self.prompt_credential()
        self.database.add(**credential)
        self.display = self.database.credentials

    def get_credentials(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)

    def search_credentials(self, query):
        self.display = self.database.search(query=query)

    def remove_credentials(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)
        if not self.display:
            return self.write(
                "No credentials found for `{}`".format(fullname),
                error=True
            )

        self.show_display()
        confirmed = self.prompt_confirmation("Remove these credentials?")
        if confirmed:
            self.database.remove(name=name, login=login)
            self.display = self.database.credentials

    def update_credentials(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)
        if not self.display:
            return self.write(
                "No credentials found for `{}`".format(fullname),
                error=True
            )

        self.show_display()
        confirmed = self.prompt_confirmation("Edit these credentials?")
        if confirmed:
            values = self.prompt_credential()
            clean_values = {k: v for k, v in values.items() if v}
            self.display = self.database.update(
                name=name,
                login=login,
                to_update=clean_values
            )
        else:
            self.display = []

    def copy_to_clipboard(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)
        if not self.display:
            return self.write(
                "No credentials found for `{}`".format(fullname),
                True
            )
        elif len(self.display) == 1:
            credential = self.display[0]
            passphrase = self.get_passphrase()
            password = self.database.gpg.decrypt(
                credential.password,
                passphrase=passphrase
            )
            pyperclip.copy(password)
            cred_string = "Password for '{}' copied to clipboard".format(
                asfullname(credential.name, credential.login)
            )
            self.write(cred_string)
            self.display = []
        elif len(self.display) > 1:
            print("-- Multiple credentials were found: try fullname syntax"
                  "\nfor example: login@name")

    def write(self, text, error=False):
        print("{}{}".format("-- " if error else "", text))
