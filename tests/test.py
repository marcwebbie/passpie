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


def mock_create_keys(path, *args, **kwargs):
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


@patch("pysswords.db.create_keys", new=mock_create_keys)
class DBTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(TEST_DATA_DIR, "database")
        self.keys_path = os.path.join(self.path, ".keys")
        self.passphrase = "dummy_passphrase"
        self.credential = pysswords.db.Credential(
            name="example.com",
            login="john.doe",
            password="--BEGIN GPG-- something --END GPG--",
            comment="Main email"
        )
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_create_makedirs_at_path(self):
        test_path = os.path.join(self.path, "creation")
        pysswords.db.create(path=test_path)
        self.assertTrue(os.path.exists(test_path))

    def test_create_keyring_adds_gpg_keys_to_path(self):
        pysswords.db.create_keyring(
            path=self.path,
            passphrase=self.passphrase)
        pubring = os.path.join(self.path, ".keys", "pubring.gpg")
        secring = os.path.join(self.path, ".keys", "secring.gpg")
        self.assertTrue(os.path.isfile(pubring))
        self.assertTrue(os.path.isfile(secring))

    def test_create_keyring_adds_key_to_keyring(self):
        pysswords.db.create_keyring(
            path=self.path,
            passphrase=self.passphrase)
        gpg = gnupg.GPG(homedir=self.keys_path)
        self.assertEqual(1, len(gpg.list_keys()))

    def test_create_keys_return_valid_key(self):
        key = pysswords.db.create_keys(self.path, self.passphrase)
        self.assertIsNotNone(key)

    def test_key_input_returns_batch_string_with_passphrase(self):
        batch = pysswords.db.key_input(self.path, self.passphrase)
        self.assertIn("\nPassphrase: {}".format(self.passphrase), batch)

    def test_keys_path_returns_database_path_joined_with_dot_keys(self):
        keys_path = pysswords.db.keys_path(self.path)
        self.assertEqual(keys_path, os.path.join(self.path, ".keys"))

    def test_add_credential_make_dir_in_dbpath_with_credential_name(self):
        pysswords.db.add_credential(self.path, self.credential)
        credential_dir = os.path.join(self.path, self.credential.name)
        self.assertTrue(os.path.exists(credential_dir))
        self.assertTrue(os.path.isdir(credential_dir))

    def test_add_credential_creates_pyssword_file_named_after_login(self):
        pysswords.db.add_credential(self.path, self.credential)
        credential_dir = os.path.join(self.path, self.credential.name)
        credential_filename = "{}.pyssword".format(self.credential.login)
        credential_file = os.path.join(credential_dir, credential_filename)
        self.assertTrue(os.path.isfile(credential_file))
        with open(credential_file) as f:
            self.assertEqual(yaml.load(f.read()), self.credential)

    def test_getgpg_returns_valid_gnupg_gpg_object(self):
        gpg = pysswords.db.getgpg(self.path)
        self.assertIsInstance(gpg, pysswords.db.gnupg.GPG)

    def test_pyssword_content_returns_yaml_content_parseable_to_dict(self):
        content = pysswords.db.pyssword_content(self.credential)
        self.assertEqual(yaml.load(content), self.credential)


if __name__ == "__main__":
    if sys.version_info >= (3,):
        unittest.main(warnings=False)
    else:
        unittest.main()
