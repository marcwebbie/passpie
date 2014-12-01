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
        self.password = "=Sup3rh4rdp4ssw0rdt0cr4ck"

    def tearDown(self):
        os.remove(self.tmp_db_file.name)

    def test_create_credential_database(self):
        db_path = self.tmp_db_file.name

        db = pysswords.PysswordDB(db_path=db_path, password=self.password)
        self.assertIsNotNone(db)

    def test_create_valid_pyssword_dabatase_file(self):
        db_path = self.tmp_db_file.name
        db = pysswords.PysswordDB(db_path=db_path, password=self.password)
        self.assertTrue(db.valid)

    def test_add_new_credential(self):
        db_path = self.tmp_db_file.name
        db = pysswords.PysswordDB(db_path=db_path, password=self.password)
        self.assertEqual(db.count, 0)

        credential = pysswords.Credential(
            name="example",
            login="john",
            password="my-great-password",
            login_url="http://example.org/login",
            description="This is login credentials for example"
        )
        db.add_credential(credential)
        self.assertEqual(db.count, 1)

    def test_get_credentials_by_name(self):
        db_path = self.tmp_db_file.name
        db = pysswords.PysswordDB(db_path=db_path, password=self.password)

        credential = pysswords.Credential(
            name="example",
            login="john",
            password="my-great-password",
            login_url="http://example.org/login",
            description="This is login credentials for example"
        )
        db.add_credential(credential)
        found_credential = db.get_credential(name="example")

        self.assertEqual(credential, found_credential)

if __name__ == "__main__":
    unittest.main()
