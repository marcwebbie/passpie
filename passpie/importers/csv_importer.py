import csv
from passpie.importers import BaseImporter


def get_csv_rows(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    rows = []
    for row in csv_reader:
        cells = []
        for cell in row:
            try:
                # python2
                cell = cell.decode("utf-8")
            except AttributeError:
                pass
            cells.append(cell)
        rows.append(cells)
    return rows


class CSVImporter(BaseImporter):

    def match(self, filepath):
        """Dont match this importer"""
        return False

    def handle(self, filepath, params):
        cols = params.get("cols")
        skip_lines = params.get("skip_lines")
        credentials = []
        with open(filepath) as csv_file:
            rows = get_csv_rows(csv_file)
            if not rows:
                raise ValueError('empty csv file: %s' % filepath)
            for row in rows[skip_lines:]:
                name_index = cols['name']
                login_index = cols['login']
                password_index = cols['password']
                comment_index = cols.get('comment')
                credential = {
                    'name': row[name_index],
                    'login': row[login_index],
                    'password': row[password_index],
                    'comment': row[comment_index] if comment_index else "",
                }
                credentials.append(credential)
        return credentials
