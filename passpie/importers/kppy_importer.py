from datetime import datetime
import os

import click

try:
    import kppy
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

        return True

    def handle(self, filepath):
    	pass
