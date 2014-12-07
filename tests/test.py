import argparse
import json
import os
import runpy
import sys
from tempfile import NamedTemporaryFile
import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pysswords.db import Database, Credential
from pysswords.crypt import CryptOptions
import pysswords.__main__

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = EnvironmentError

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


class PysswordsTests(unittest.TestCase):
    def setUp(self):
        self.db_file = NamedTemporaryFile(mode='w', delete=False)
        self.db_path = self.db_file.name
        self.testing_path = os.path.join(TEST_DIR,
                                         "data",
                                         "testing_database.db")
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

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.testing_path)
        except FileNotFoundError:
            pass

    def some_credential(self, **kwargs):
        return Credential(
            name=kwargs.get("name", "example"),
            login=kwargs.get("login", "john"),
            password=kwargs.get("password", "my-great-password"),
            login_url=kwargs.get("login_url", "http://example.org/login"),
            description=kwargs.get("description",
                                   "This is login credentials for example"),
        )

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
        self.assertEqual(len(self.db.credentials), 0)

    def test_delete_credential_by_name_and_login(self):
        credential = self.some_credential(name="github", login="example")
        credential2 = self.some_credential(name="github", login="john")

        self.db.add_credential(credential)
        self.db.add_credential(credential2)

        self.db.delete_credential(name=credential2.name,
                                  login=credential2.login)

        self.assertIn(credential, self.db.credentials)
        self.assertNotIn(credential2, self.db.credentials)

    def test_find_credentials_by_name(self):
        credential = self.some_credential(name="Amazing Name")
        self.db.add_credential(credential)
        self.db.add_credential(credential)
        self.db.find_credentials(name=credential.name)

        self.assertIn(credential, self.db.credentials)
        self.assertEqual(len(self.db.credentials), 2)

    def test_find_credentials_by_login(self):
        credential = self.some_credential(login="john")
        self.db.add_credential(credential)
        self.db.find_credentials(login=credential.login)

        self.assertIn(credential, self.db.credentials)
        self.assertEqual(len(self.db.credentials), 1)

    def test_find_credentials_by_name_and_login(self):
        credential = self.some_credential(name="github", login="example")
        credential2 = self.some_credential(name="github", login="john")

        self.db.add_credential(credential)
        self.db.add_credential(credential2)
        credentials = self.db.find_credentials(name=credential.name,
                                               login=credential.login)

        self.assertIn(credential, self.db.credentials)
        self.assertEqual(len(credentials), 1)

    def test_verify_creates_valid_database_with_password(self):
        database_path = self.testing_path
        database = Database.create(
            path=database_path,
            crypt_options=self.crypt_options
        )

        verify_result = Database.verify(database.path, self.password)
        self.assertTrue(verify_result)
        bad_password = "notvalidpasswordfordatabase"
        verify_bad_result = Database.verify(database.path, bad_password)
        self.assertFalse(verify_bad_result)


class ConsoleInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(TEST_DIR,
                                 "data",
                                 "testing_database.db")
        self.args = argparse.Namespace(
            path=self.path,
            create=False,
            add=False,
            password="password",
            iterations=1000,
            salt=None
        )
        self.PatcherDatabase = patch(
            "pysswords.__main__.Database"
        )
        self.PatcherCryptOptions = patch(
            "pysswords.__main__.CryptOptions",
            return_value=CryptOptions(
                password=self.args.password,
                salt=None,
                iterations=1000
            )
        )
        self.PatcherCredential = patch(
            "pysswords.__main__.Credential",
            return_value=Credential(
                name="example",
                login="john",
                password="great-password",
                login_url="https://example.com/login",
                description="Credentials to example.com",
            )
        )
        self.MockCryptOptions = self.PatcherCryptOptions.start()
        self.MockDatabase = self.PatcherDatabase.start()
        self.MockCredential = self.PatcherCredential.start()

    def tearDown(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass

        self.PatcherCryptOptions.stop()
        self.PatcherDatabase.stop()

    def test_get_args_throw_errors_when_no_argument_is_set(self):
        with open(os.devnull, 'w') as devnull:
            with patch('sys.stderr', devnull):
                with self.assertRaises(SystemExit):
                    pysswords.__main__.get_args()

    def test_main_is_called_when_main_module_is_run_as_main(self):
        with open(os.devnull, 'w') as devnull:
            with patch('sys.stderr', devnull):
                with self.assertRaises(SystemExit):
                    runpy._run_module_as_main("pysswords.__main__")

    def test_interface_calls_create_when_create_args_is_passed(self):
        self.args.create = True
        pysswords.__main__.main(args=self.args)
        self.MockDatabase.create.assert_called_with(
            self.path,
            self.MockCryptOptions()
        )

    def test_main_get_credential_is_called_when_add_arg_passed(self):
        self.args.add = True

        # with patch('__builtin__.input') as mock_input:
        if sys.version_info < (3,):
            input_function = "pysswords.__main__.input"
        else:
            input_function = "builtins.input"

        with patch(input_function) as mock_input:
            with patch("pysswords.__main__.getpass"):
                pysswords.__main__.main(args=self.args)
                self.assertTrue(mock_input.called)

    def test_main_get_password_raises_value_error_password_dont_match(self):
        self.args.add = True
        mock_passwords = ["password", "p4ssw0rd"] * 3
        with patch("pysswords.__main__.getpass", side_effect=mock_passwords):
            with open(os.devnull, 'w') as devnull:
                with patch("sys.stderr", devnull):
                    with self.assertRaises(ValueError):
                        pysswords.__main__.create_password()

    def test_interface_calls_add_credential_when_add_args_true(self):
        self.args.add = True

        func_mock = "pysswords.__main__.get_credential"
        with patch(func_mock, return_value=self.MockCredential()):
            with patch("pysswords.__main__.getpass", return_value=""):
                pysswords.__main__.main(args=self.args)
                self.MockDatabase().add_credential.assert_called_with(
                    self.MockCredential()
                )

    def test_console_interface_asks_for_password_when_no_password(self):
        self.args.password = None
        with patch('pysswords.__main__.getpass') as patched_getpass:
            pysswords.__main__.main(args=self.args)
            self.assertTrue(patched_getpass.called)

if __name__ == "__main__":
    unittest.main()
