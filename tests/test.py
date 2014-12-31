import inspect
import os
import shutil
import sys
import unittest
import yaml
try:
    from unittest.mock import patch
except ImportError:
    try:
        from mock import patch
    except ImportError:
        exit("mock not found. Run: `pip install mock`")

import gnupg


__file__ = os.path.relpath(inspect.getsourcefile(lambda _: None))

TEST_DIR = os.path.join(os.path.dirname(os.path.relpath(__file__)))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.relpath(__file__))))
import pysswords


def mock_create_keys(self, path, *args, **kwargs):
    """Import key.asc instead of generating new key
    passphrase used to create the key was 'dummy_database'"""
    gpg = gnupg.GPG(homedir=path)
    with open(os.path.join(TEST_DATA_DIR, "key.asc")) as keyfile:
        gpg.import_keys(keyfile.read())
    return gpg.list_keys()[0]


def some_credential(**kwargs):
    return pysswords.db.Credential(
        name=kwargs.get("name", "example.com"),
        login=kwargs.get("login", "john.doe"),
        password=kwargs.get("password", "--BEGIN GPG-- X --END GPG--"),
        comment=kwargs.get("comment", "Some comments"),
    )


@patch("pysswords.db.Database.create_keys", new=mock_create_keys)
class DBTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(TEST_DATA_DIR, "database")
        self.keys_path = os.path.join(self.path, ".keys")
        self.passphrase = "dummy_passphrase"
        self.database = pysswords.db.Database.create(self.path)
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_create_makedirs_at_path(self):
        test_path = os.path.join(self.path, "creation")
        pysswords.db.Database.create(path=test_path)
        self.assertTrue(os.path.exists(test_path))

    def test_create_return_database_instance(self):
        database = pysswords.db.Database.create(self.path)
        self.assertIsInstance(database, pysswords.db.Database)

    def test_create_keyring_adds_gpg_keys_to_path(self):
        self.database.create_keyring(passphrase=self.passphrase)
        pubring = os.path.join(self.path, ".keys", "pubring.gpg")
        secring = os.path.join(self.path, ".keys", "secring.gpg")
        self.assertTrue(os.path.isfile(pubring))
        self.assertTrue(os.path.isfile(secring))

    def test_create_keyring_adds_key_to_keyring(self):
        self.database.create_keyring(passphrase=self.passphrase)
        gpg = gnupg.GPG(homedir=self.keys_path)
        self.assertEqual(1, len(gpg.list_keys()))

    def test_create_keys_return_valid_key(self):
        key = self.database.create_keys(self.path, self.passphrase)
        self.assertIsNotNone(key)

    def test_key_input_returns_batch_string_with_passphrase(self):
        batch = self.database.key_input(self.passphrase)
        self.assertIn("\nPassphrase: {}".format(self.passphrase), batch)

    def test_keys_path_returns_database_path_joined_with_dot_keys(self):
        keys_path = self.database.keys_path
        self.assertEqual(keys_path, os.path.join(self.path, ".keys"))

    def test_add_credential_make_dir_in_dbpath_with_credential_name(self):
        self.database.add(some_credential())
        credential_dir = os.path.join(self.path, some_credential().name)
        self.assertTrue(os.path.exists(credential_dir))
        self.assertTrue(os.path.isdir(credential_dir))

    def test_add_credential_createas_pyssword_file_named_after_login(self):
        credential = some_credential()
        self.database.add(credential)
        credential_dir = os.path.join(self.path, credential.name)
        credential_filename = "{}.pyssword".format(credential.login)
        credential_file = os.path.join(credential_dir, credential_filename)
        self.assertTrue(os.path.isfile(credential_file))
        with open(credential_file) as f:
            self.assertEqual(yaml.load(f.read()), credential)

    def test_add_credential_creates_dir_when_credential_name_is_a_valid_dir(self):
        credential = some_credential(name="emails/misc/example.com")
        emails_dir = os.path.join(self.path, "emails")
        misc_dir = os.path.join(emails_dir, "misc")
        self.database.add(credential)
        self.assertTrue(os.path.isdir(emails_dir))
        self.assertTrue(os.path.isdir(misc_dir))

    def test_add_credential_returns_credential_path(self):
        credential = some_credential()
        credential_path = self.database.add(credential)
        expected_path = os.path.join(
            self.path,
            os.path.basename(credential.name),
            "{}.pyssword".format(credential.login)
        )
        self.assertEqual(credential_path, expected_path)

    def test_gpg_returns_valid_gnupg_gpg_object(self):
        gpg = self.database.gpg
        self.assertIsInstance(gpg, pysswords.db.gnupg.GPG)

    def test_pyssword_content_returns_yaml_content_parseable_to_dict(self):
        content = pysswords.db.Database.content(some_credential())
        self.assertEqual(yaml.load(content), some_credential())

    def test_credentials_returns_a_list_of_all_added_credentials(self):
        self.database.add(some_credential(name="example.com"))
        self.database.add(some_credential(name="archive.org"))
        credentials = self.database.credentials
        self.assertIsInstance(credentials, list)
        self.assertEqual(2, len(credentials))
        for credential in credentials:
            self.assertIsInstance(credential, pysswords.db.Credential)

    def test_credential_path_returns_expected_path_to_credential(self):
        credential = some_credential()
        credential_path = self.database._credential_path(credential)
        expected_path = os.path.join(
            self.path,
            os.path.basename(credential.name),
            "{}.pyssword".format(credential.login)
        )
        self.assertEqual(credential_path, expected_path)

if __name__ == "__main__":
    if sys.version_info >= (3,):
        unittest.main(warnings=False)
    else:
        unittest.main()
