import inspect
import os
import shutil
import sys
import unittest
from unittest.mock import patch

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


@patch("pysswords.db.create_keys", new=mock_create_keys)
class DBTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(TEST_DATA_DIR, "database")
        self.keys_path = os.path.join(self.path, ".keys")
        self.passphrase = "dummy_passphrase"
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
        batch = pysswords.db.key_input(self.passphrase)
        self.assertIn("\nPassphrase: {}".format(self.passphrase), batch)

    def test_keys_path_returns_database_path_joined_with_dot_keys(self):
        keys_path = pysswords.db.keys_path(self.path)
        self.assertEqual(keys_path, os.path.join(self.path, ".keys"))


if __name__ == "__main__":
    unittest.main(warnings=False)
