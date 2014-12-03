import os
import sys
from tempfile import NamedTemporaryFile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pysswords import db

class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.tmp_db_file = NamedTemporaryFile(mode='w', delete=False)
        self.tmp_db_file.close()
        self.password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        self.default_iterations = 1000

    def tearDown(self):
        os.remove(self.tmp_db_file.name)

    def test_create_credential_database(self):
        db_path = self.tmp_db_file.name

        created_path = db.create(
            db_path=db_path,
            password=self.password,
            iterations=self.default_iterations
        )
        self.assertEqual(created_path, db_path)

if __name__ == "__main__":
    unittest.main()
