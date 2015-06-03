import os

import click

try:
    from kppy.database import KPDBv1
    from kppy.entries import v1Entry
    from kppy.exceptions import KPError
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
                    group_names_str = self.compute_group_name(entry)

                    entry_fullname = make_fullname(
                        entry.username, group_names_str)

                    credential_dict = {
                        'fullname': entry_fullname,
                        'name': group_names_str,
                        'login': entry.username,
                        'password': entry.password,
                        'comment': entry.comment,
                        'modified': entry.creation,
                    }
                    credentials.append(credential_dict)

                return credentials
            finally:
                db.close()

    @staticmethod
    def compute_group_name(kp_entry):
        if not isinstance(kp_entry, v1Entry):
            raise TypeError('kp_entry is not a kppy.entries.v1Entry')

        group_names = [kp_entry.url]

        group = kp_entry.group
        while group:
            if group.title:
                group_names.insert(0, group.title)
            group = group.parent

        group_names_str = '/'.join(
            e.strip() for e in group_names if e)

        return group_names_str