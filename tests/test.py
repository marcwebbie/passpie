import os
import sys
from tempfile import NamedTemporaryFile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pysswords.db import Database

class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.db_file = NamedTemporaryFile(mode='w', delete=False)
        self.db_path = self.db_file.name
        self.db_file.close()
        self.password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        self.default_iterations = 1000

        self.db = Database.create(
            db_path=self.db_path,
            password=self.password,
            iterations=self.default_iterations
        )

    def tearDown(self):
        os.remove(self.db_path)

    def test_create_credential_database(self):
        database = Database.create(
            db_path=self.db_path,
            password=self.password,
            iterations=self.default_iterations
        )
        self.assertIsNotNone(database)

    # def test_add_new_credential(self):
    #     db_path = self.db_file.name

    #     credential = db.Credential(
    #         name="example",
    #         login="john",
    #         password="my-great-password",
    #         login_url="http://example.org/login",
    #         description="This is login credentials for example"
    #     )
    #     db.add_credential(db_path, credential)
    #     self.assertEqual(db.count, 1)


if __name__ == "__main__":
    unittest.main()
