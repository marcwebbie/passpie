import os
import sys
from tempfile import NamedTemporaryFile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pysswords

class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.tmp_db_file = NamedTemporaryFile(mode='w', delete=False)
        self.tmp_db_file.close()

    def tearDown(self):
        os.remove(self.tmp_db_file.name)

    def test_create_credential_database(self):
        db_path = self.tmp_db_file.name

        password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        db = pysswords.PysswordDB(db_path=db_path, password=password)
        self.assertIsNotNone(db)

    def test_create_valid_pyssword_dabatase_file(self):
        db_path = self.tmp_db_file.name
        password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        db = pysswords.PysswordDB(db_path=db_path, password=password)
        self.assertTrue(db.is_valid(password))

    def test_is_valid_returns_false_if_wrong_password_is_given(self):
        db_path = self.tmp_db_file.name
        password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        db = pysswords.PysswordDB(db_path=db_path, password=password)
        wrong_password = "something-else"
        self.assertFalse(db.is_valid(wrong_password))


if __name__ == "__main__":
    unittest.main()
