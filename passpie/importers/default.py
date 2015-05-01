import yaml
from yaml.scanner import ScannerError

from passpie.importers import BaseImporter


class DefaultImporter(BaseImporter):

    def match(self, filepath):
        try:
            dict_content = yaml.load(open(filepath).read())
        except ScannerError as e:
            print(str(e))
            return False

        try:
            assert dict_content.get('handler') == 'passpie'
            assert isinstance(dict_content.get('version'), float)
        except AssertionError as e:
            print(str(e))
            return False

        return True

    def handle(self, filepath):
        dict_content = yaml.load(open(filepath).read())
        credentials = dict_content.get('credentials')
        return credentials
