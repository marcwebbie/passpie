import inspect
import os
import shutil
import sys
import unittest
from unittest.mock import patch

import gnupg


__file__ = os.path.abspath(inspect.getsourcefile(lambda _: None))

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        self.passphrase = "dummy_passphrase"

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
        pubring = os.path.join(self.path, "pubring.gpg")
        secring = os.path.join(self.path, "secring.gpg")
        self.assertTrue(os.path.exists(pubring))
        self.assertTrue(os.path.exists(secring))

    def test_create_keyring_adds_key_to_keyring(self):
        self.assertEqual(0, len(gnupg.GPG(homedir=self.path).list_keys()))
        pysswords.db.create_keyring(
            path=self.path,
            passphrase=self.passphrase)
        self.assertEqual(1, len(gnupg.GPG(homedir=self.path).list_keys()))

    def test_create_keys_return_valid_key(self):
        key = pysswords.db.create_keys(self.path, self.passphrase)
        self.assertIsNotNone(key)

    def test_key_input_returns_batch_string_with_passphrase(self):
        batch = pysswords.db.key_input(self.passphrase)
        self.assertIn("\nPassphrase: {}".format(self.passphrase), batch)


if __name__ == "__main__":
    unittest.main(warnings=False)
