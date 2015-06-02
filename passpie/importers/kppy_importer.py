from datetime import datetime
import os

import click

try:
    import kppy
    from kppy.database import KPDBv1
    from kppy.entries import v1Entry
    from kppy.exceptions import KPError
    from kppy.groups import v1Group
    _found_kppy = True
except ImportError:
    _found_kppy = False

from passpie.importers import BaseImporter
from passpie.credential import make_fullname


class KppyImporter(BaseImporter):

    def match(self, filepath):
        if not _found_kppy:
            self.log('kppy is not installed')
            return False

        if not os.path.isfile(filepath):
            self.log('Filepath "{}" is not a file'.format(filepath))
            return False

        if os.path.splitext(filepath)[1].lower() != '.kdb':
            self.log('Filepath "{}" is not a Keepass database'.format(filepath))
            return False

        return True

    def handle(self, filepath):
        passphrase = click.prompt('Keepass passphrase', hide_input=True)

        try:
            # TODO add keyfile support
            db = KPDBv1(filepath=str(filepath), password=str(passphrase),
                        read_only=True)
            db.load()
        except KPError as e:
            self.log(str(e))
            return []
        except Exception as e:
            self.log(str(e))
            return []
        else:
            try:
                credentials = []

                for entry in db.entries:

                    credential_dict = {
                        'fullname': make_fullname(entry.username, entry.url),
                        'name': entry.username,
                        'login': entry.username,
                        'password': entry.password,
                        'comment': entry.comment,
                        'modified': entry.creation,
                    }
                    credentials.append(credential_dict)

                return credentials
            finally:
                db.close()
