from datetime import datetime
import csv

from passpie.importers import BaseImporter
from passpie.credential import make_fullname


class PwsafeImporter(BaseImporter):

    def match(self, filepath):
        print("Hello world!")
        try:
            with open(filepath) as fp:
                file_content = fp.read()
        except OSError:
            return False

        try:
            file_header = file_content.split('\n')[0]
            assert file_header.find("passwordsafe") != -1
        except:
            return False

        return True

    def make_passpie_name(self, group, name):
        return group + name

    def handle(self, filepath):
        print("Here")
        csvfile = open(filepath, "rb")
        reader = csv.reader(csvfile, delimiter='\t', quotechar='\"')

        credentials = []

        next(reader)  # this is file fingerprint
        next(reader)  # this is table header

        for row in reader:
            # uuid = row[0] # currently unused
            group = row[1]
            name = row[2]
            login = row[3]
            passwd = row[4]
            notes = row[5]

            passpie_name = self.make_passpie_name(group, name)

            credential_dict = {
                'fullname': make_fullname(login, passpie_name),
                'name': passpie_name,
                'login': login,
                'password': passwd,
                'comment': notes,
                'modified': datetime.now(),
            }

            credentials.append(credential_dict)

        return credentials
