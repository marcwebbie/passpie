from datetime import datetime
import os

import click

from passpie.importers import BaseImporter
from passpie.credential import make_fullname


class PysswordImporter(BaseImporter):

    def match(self, filepath):
        if '.keys' not in os.listdir(filepath):
            return False

        try:
            from pysswords.db import Database
        except ImportError:
            return False

        return True

    def handle(self, filepath):
        from pysswords.db import Database
        # import pudb; pudb.set_trace()

        db = Database(path=filepath)
        passphrase = click.prompt('Pysswords passphrase', hide_input=True)
        if not db.check(passphrase):
            return False

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
