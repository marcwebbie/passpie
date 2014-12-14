import os
import shutil
import sys
import unittest
import gnupg

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pysswords.db
import pysswords.crypt


class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(TEST_DIR, ".pysswords")
        self.gnupg_path = os.path.join(self.database_path, ".gnupg")
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
        self.assertTrue(os.path.exists(self.database_path))
        self.assertTrue(os.path.exists(self.gnupg_path))


class PysswordsCryptTests(unittest.TestCase):
    def setUp(self):
        self.database_path = os.path.join(TEST_DIR, ".pysswords")
        self.gnupg_path = os.path.join(self.database_path, ".gnupg")
        os.makedirs(self.database_path)
        self.gpg = pysswords.crypt.get_gpg(self.gnupg_path)

    def tearDown(self):
        shutil.rmtree(self.database_path)

    def test_get_gpg_creates_keyrings_in_database_path(self):
        pysswords.crypt.get_gpg(self.gnupg_path)
        self.assertIn("pubring.gpg", os.listdir(self.gnupg_path))
        self.assertIn("secring.gpg", os.listdir(self.gnupg_path))

    def test_get_gpg_return_valid_gpg_object(self):
        gpg = pysswords.crypt.get_gpg(self.gnupg_path)
        self.assertIsInstance(gpg, gnupg.GPG)

if __name__ == "__main__":
    if sys.version_info >= (3, 1):
        unittest.main(warnings="ignore")
    else:
        unittest.main()
