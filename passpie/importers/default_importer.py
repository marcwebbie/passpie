import yaml
from yaml.reader import ReaderError
from yaml.scanner import ScannerError

from passpie.importers import BaseImporter


class DefaultImporter(BaseImporter):

    def match(self, filepath):
        try:
            with open(filepath) as fp:
                file_content = fp.read()
        except OSError:
            return False

        try:
            dict_content = yaml.load(file_content)
        except (ReaderError, ScannerError):
            return False

        try:
            assert dict_content.get('handler') == 'passpie'
            assert isinstance(dict_content.get('version'), float)
        except AssertionError:
            return False

        return True

    def handle(self, filepath):
        with open(filepath) as fp:
            file_content = fp.read()
        dict_content = yaml.load(file_content)
        credentials = dict_content.get('credentials')
        return credentials
