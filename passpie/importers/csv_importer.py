import csv
from passpie.importers import BaseImporter


class CSVImporter(BaseImporter):

    def match(self, filepath):
        """Dont match this importer"""
        return False

    def handle(self, filepath, cols):
        credentials = []
        with open(filepath) as csv_file:
            reader = csv.reader(csv_file)
            try:
                next(reader)
            except StopIteration:
                raise ValueError('empty csv file: %s' % filepath)
            for row in reader:
                credential = {
                    'name': row[cols['name']],
                    'login': row[cols.get('login', '')],
                    'password': row[cols['password']],
                    'comment': row[cols.get('comment', '')],
                }
                credentials.append(credential)
        return credentials
