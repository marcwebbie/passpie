from getpass import getpass
import colorama
import pyperclip
from tabulate import tabulate

from .python_two import input
from .db.credential import splitname, asfullname
from .db import(
    Database,
    Credential,
    CredentialExistsError,
    CredentialNotFoundError
)


class CLI(object):

    class WrongPassphraseError(Exception):
        pass

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
        passphrase = CLI.prompt("Passphrase for database: ", password=True)
        database = Database.create(path, passphrase)
        cls.write("Database created at `{}`".format(path))
        return database

    @classmethod
    def write(cls, text, error=False):
        print("{}{}".format("-- " if error else "", text))

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
                cls.write("Entries don't match!", error=True)

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
        else:
            raise self.WrongPassphraseError("Wrong passphrase")

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
            if passphrase is None:
                raise ValueError("Wrong passphrase.")
            else:
                self.display = self.decrypt_credentials(
                    self.display,
                    passphrase
                )

        table = []
        for credential in self.display:
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
            raise CredentialNotFoundError(
                "No credentials found for `{}`".format(fullname))

        self.show_display()
        confirmed = self.prompt_confirmation("Remove these credentials?")
        if confirmed:
            self.database.remove(name=name, login=login)
            self.display = self.database.credentials

    def update_credentials(self, fullname):
        name, login = splitname(fullname)
        try:
            self.display = self.database.get(name=name, login=login)
        except CredentialNotFoundError:
            raise CredentialNotFoundError(
                "No credentials found for `{}`".format(fullname))

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
        self.display = []
        try:
            found_credentials = self.database.get(name=name, login=login)
        except CredentialNotFoundError:
            raise CredentialNotFoundError(
                "No credentials found for `{}`".format(fullname))

        if len(found_credentials) > 1:
            raise ValueError("Multiple credentials were found "
                             "try fullname syntax, Example:\n"
                             "  pysswords -c -g login@name")
        else:
            credential = found_credentials[0]
            passphrase = self.get_passphrase()
            password = self.database.gpg.decrypt(
                credential.password,
                passphrase=passphrase)
            pyperclip.copy(password)
            self.write("Password for `{}` copied to clipboard".format(
                asfullname(credential.name, credential.login)))
