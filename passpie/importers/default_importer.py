import yaml
from yaml.reader import ReaderError
from yaml.scanner import ScannerError

from passpie.importers import BaseImporter
from passpie.utils import yaml_load


def has_fields(credential):
    has_required_fields = (
        "login" in credential.keys() and
        "name" in credential.keys() and
        "password" in credential.keys() and
        "comment" in credential.keys())
    if has_required_fields:
        return True
    else:
        return False


class DefaultImporter(BaseImporter):

    def match(self, filepath):
        with open(filepath) as fp:
            file_content = fp.read()
            try:
                dict_content = yaml.load(file_content)
            except (ReaderError, ScannerError):
                return False

        return all(has_fields(cred) for cred in dict_content)

    def handle(self, filepath, params):
        return yaml_load(filepath)
