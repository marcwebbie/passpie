import os

import yaml
from yaml.scanner import ScannerError

from passpie.importers import BaseImporter


class DefaultImporter(BaseImporter):

    def _read_file(self, filepath):
        return open(filepath).read()

    def match(self, filepath):
        if not os.path.isfile(filepath):
            return False

        try:
            dict_content = yaml.load(self._read_file(filepath))
        except ScannerError:
            return False

        try:
            assert dict_content.get('handler') == 'passpie'
            assert isinstance(dict_content.get('version'), float)
        except AssertionError:
            return False

        return True

    def handle(self, filepath):
        dict_content = yaml.load(self._read_file(filepath))
        credentials = dict_content.get('credentials')
        return credentials
