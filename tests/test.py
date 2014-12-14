import os
import shutil
import sys
import unittest

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pysswords.db


class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(TEST_DIR, "data")
        pysswords.db.init(database_path=self.database_path)

    def tearDown(self):
        shutil.rmtree(self.database_path)

    def some_credential(self, **kwargs):
        return {
            "name": kwargs.get("name", "example"),
            "login": kwargs.get("login", "john"),
            "password": kwargs.get("password", "my-great-password"),
            "login_url": kwargs.get("login_url", "http://example.org/login"),
            "description": kwargs.get("description",
                                      "This is login credentials for example"),
        }

    def test_init_database_creates_gnupg_hidden_directory(self):
        gnupg_path = os.path.join(self.database_path, ".gnupg")
        self.assertTrue(os.path.exists(self.database_path))
        self.assertTrue(os.path.exists(gnupg_path))

if __name__ == "__main__":
    unittest.main()
