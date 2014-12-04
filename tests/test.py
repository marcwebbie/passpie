import json
import os
import sys
from tempfile import NamedTemporaryFile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pysswords.db import Database, Credential
from pysswords.crypt import CryptOptions


class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.db_file = NamedTemporaryFile(mode='w', delete=False)
        self.db_path = self.db_file.name
        self.db_file.close()
        self.password = "=Sup3rh4rdp4ssw0rdt0cr4ck"
        self.default_iterations = 1000

        self.crypt_options = CryptOptions(
            password=self.password,
            salt=None,
            iterations=1000
        )

        self.db = Database.create(
            path=self.db_path,
            crypt_options=self.crypt_options
        )

    def some_credential(self, **kwargs):
        return Credential(
            name=kwargs.get("name", "example"),
            login=kwargs.get("login", "john"),
            password=kwargs.get("password", "my-great-password"),
            login_url=kwargs.get("login_url", "http://example.org/login"),
            description=kwargs.get("description", "This is login credentials for example"),
        )

    def tearDown(self):
        os.remove(self.db_path)

    def test_database_default_content(self):
        expected_content = json.dumps([{}])
        self.assertEqual(Database.DEFAULT_CONTENT, expected_content)

    def test_create_credential_database(self):
        database = Database.create(
            path=self.db_path,
            crypt_options=self.crypt_options
        )
        self.assertIsInstance(database, Database)
        self.assertEqual(len(database.credentials), 0)

    def test_add_new_credential(self):
        self.assertEqual(len(self.db.credentials), 0)
        self.db.add_credential(self.some_credential())
        self.assertEqual(len(self.db.credentials), 1)

    def test_delete_credential_by_name(self):
        self.db.add_credential(self.some_credential(name="example"))
        self.db.delete_credential(name="example")
        self.assertEqual(len(self.db.credentials), 0)

    def test_delete_credential_by_login(self):
        self.db.add_credential(self.some_credential(login="john"))
        self.db.delete_credential(login="john")
        self.assertEqual(len(self.db.credentials), 0, "Couldn't delete credential")

    def test_delete_credential_by_name_and_login(self):
        credential = self.some_credential(name="github", login="example")
        credential2 = self.some_credential(name="github", login="john")

        self.db.add_credential(credential)
        self.db.add_credential(credential2)
        self.db.delete_credential(name=credential2.name, login=credential2.login)

        self.assertIn(credential, self.db.credentials)
        self.assertNotIn(credential2, self.db.credentials)





if __name__ == "__main__":
    unittest.main()
