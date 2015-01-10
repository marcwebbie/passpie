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

    def create_database(self, path):
        passphrase = CLI.prompt("Passhprase for database", password=True)
        database = Database.create(path, passphrase)
        return database

    def prompt_password(self, text):
        for _ in range(3):
            password = getpass(text)
            repeat_password = getpass("Type again: ")
            if password == repeat_password:
                return password
            else:
                print("Entries don't match!")
        else:
            raise ValueError("Entries didn't match")

    def prompt(self, text, default=None, password=False):
        if password:
            self.prompt_password(text)
        else:
            entry = input("{}{}: ".format(
                text,
                "[{}]".format(default) if default else "")
            )
            return entry

    def prompt_credential(self, **defaults):
        credential_dict = {
            "name": self.prompt("Name", defaults.get("name")),
            "login": self.prompt("Login", defaults.get("login")),
            "password": self.prompt("Password", defaults.get("password")),
            "comment": self.prompt("Comment", defaults.get("comment"))
        }
        return credential_dict

    def prompt_confirmation(self, text):
        entry = input("{} (y|n): ".format(text))
        if entry and entry.lower().startswith("y"):
            return True
        else:
            return False

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
            passphrase = getpass("Passphrase: ")
            if self.database.check(passphrase):
                credentials = self.decrypt_credentials(
                    self.display,
                    passphrase
                )
            else:
                print("-- Wrong passphrase")
                return
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
        self.display = self.database.search(query)

    def remove_credentials(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)
        if not self.display:
            return

        self.show_display()
        confirmed = self.prompt_confirmation("Remove these credentials?")
        if confirmed:
            self.database.remove(name, login)
            self.display = self.database.credentials

    def update_credentials(self, fullname):
        name, login = splitname(fullname)
        self.display = self.database.get(name=name, login=login)
        if not self.display:
            return

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
        if len(self.display) == 1:
            credential = self.display[0]
            passphrase = getpass("Passphrase: ")
            password = self.database.gpg.decrypt(
                credential.password,
                passphrase=passphrase
            )
            pyperclip.copy(password)
            cred_string = "Password for '{}' copied to clipboard".format(
                asfullname(credential.name, credential.login)
            )
            print(cred_string)
            self.display = []
        elif len(self.display) > 1:
            print("--Multiple credentials where found: try fullname syntax"
                  "\nfor example: login@name")
        else:
            self.display = []
