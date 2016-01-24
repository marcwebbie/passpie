from datetime import datetime
import os

import click

from passpie.importers import BaseImporter
from passpie.credential import make_fullname

try:
    from pysswords.db import Database

    def found_pysswords():
        return True
except ImportError:
    def found_pysswords():
        return False


class PysswordsImporter(BaseImporter):

    def match(self, filepath):
        if not found_pysswords():
            self.log('Pysswords is not installed')
            return False

        try:
            assert os.path.isdir(filepath)
            assert '.keys' in os.listdir(filepath)
        except AssertionError:
            self.log('.keys not found in path')
            return False

        return True

    def handle(self, filepath):
        db = Database(path=filepath)
        passphrase = click.prompt('Pysswords passphrase', hide_input=True)
        if not db.check(passphrase):
            return []

        credentials = []
        for cred in db.credentials:
            credential_dict = {
                'fullname': make_fullname(cred.login, cred.name),
                'name': cred.name,
                'login': cred.login,
                'password': db.decrypt(cred.password, passphrase),
                'comment': cred.comment,
                'modified': datetime.now(),
            }
            credentials.append(credential_dict)

        return credentials
