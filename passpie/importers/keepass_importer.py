from passpie.importers import BaseImporter
from .csv_importer import unicode_csv_reader


class KeepassImporter(BaseImporter):

    def match(self, filepath):
        expected_headers = ['Group', 'Title', 'Username', 'Password', 'URL', 'Notes']
        with open(filepath) as csv_file:
            reader = unicode_csv_reader(csv_file)
            try:
                headers = next(reader)
            except StopIteration:
                raise ValueError('empty csv file: %s' % filepath)
            return headers == expected_headers
        return False

    def handle(self, filepath, **kwargs):
        credentials = []
        with open(filepath) as csv_file:
            reader = unicode_csv_reader(csv_file)
            try:
                next(reader)
            except StopIteration:
                raise ValueError('empty csv file: %s' % filepath)
            for row in reader:
                credential = {
                    'name': row[4],
                    'login': row[2],
                    'password': row[3],
                    'comment': row[5],
                }
                credentials.append(credential)
        return credentials
