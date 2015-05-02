import os

from passpie.crypt import Cryptor, KEY_INPUT
from passpie._compat import which, FileNotFoundError, FileExistsError
from .helpers import MockerTestCase


class CryptTests(MockerTestCase):

    def setUp(self):
        self.mock_gnupg = self.patch("passpie.crypt.gnupg")
        self.mock_tempfile = self.patch("passpie.crypt.tempfile")
        self.mock_shutil = self.patch("passpie.crypt.shutil")

    def test_cryptor_initialization(self):
        path = "path/to/database"
        cryptor = Cryptor(path)
        self.assertEqual(cryptor.path, path)
        self.assertEqual(cryptor.keys_path, os.path.join(path, ".keys"))
        self.assertEqual(cryptor._binary, which("gpg"))
        self.assertEqual(cryptor._homedir, self.mock_tempfile.mkdtemp())
        self.assertEqual(cryptor._gpg, self.mock_gnupg.GPG())

    def test_cryptor__enter__returns_self(self):
        cryptor = Cryptor("path/to/database")
        self.assertEqual(Cryptor.__enter__(cryptor), cryptor)

    def test_cryptor__exit__removes_homedir_temp_directory(self):
        with Cryptor("path/to/database") as cryptor:
            homedir = cryptor._homedir
        self.mock_shutil.rmtree.assert_called_once_with(homedir)

    def test_import_keys_opens_keys_path_and_import_to_gpg(self):
        to_patch = 'passpie.crypt.open'
        mock_open = self.patch(to_patch, self.mock_open(), create=True)
        mock_open().read.return_value = "key data"

        cryptor = Cryptor("path/to/database")
        cryptor._import_keys()
        cryptor._gpg.import_keys.assert_called_once_with(
            mock_open().read()
        )

    def test_import_keys_raises_file_not_found_when_keys_not_found(self):
        to_patch = 'passpie.crypt.open'
        mock_open = self.patch(to_patch, self.mock_open(), create=True)
        cryptor = Cryptor("path/to/database")

        mock_open.side_effect = OSError(2, "File Not Found")
        with self.assertRaises(FileNotFoundError):
            cryptor._import_keys()

        mock_open.side_effect = OSError(17, "File exists")
        try:
            cryptor._import_keys()
        except Exception as exc:
            self.assertNotIsInstance(exc, FileNotFoundError)

    def test_key_returns_current_key_fingerprint(self):
        cryptor = Cryptor("path/to/database")
        curkey = cryptor._gpg.list_keys().curkey

        self.assertEqual(cryptor.current_key, curkey["fingerprint"])

    def test_create_keys_raises_file_exist_error_when_keys_found_in_path(self):
        cryptor = Cryptor("path/to/database")
        self.patch("passpie.crypt.os.path.exists",
                   self.Mock(return_value=True))

        with self.assertRaises(FileExistsError):
            cryptor.create_keys("passphrase")

    def test_create_keys_export_public_and_secret_keys_into_keyspath(self):
        cryptor = Cryptor("path/to/database")
        passphrase = "passphrase"
        self.patch("passpie.crypt.os.path.exists",
                   self.Mock(return_value=False))
        keys = self.Mock(fingerprint="HEX")
        cryptor._gpg.gen_key.return_value = keys
        mock_open = self.patch("passpie.crypt.mkdir_open",
                               self.mock_open(), create=True)
        mock_keyfile = self.Mock()
        mock_open().__enter__.return_value = mock_keyfile

        cryptor.create_keys(passphrase)

        key_input = KEY_INPUT.format(passphrase)
        cryptor._gpg.gen_key.assert_called_once_with(key_input)
        cryptor._gpg.export_keys.assert_any_call(keys.fingerprint)

        pubkey = cryptor._gpg.export_keys(keys.fingerprint)
        seckey = cryptor._gpg.export_keys(keys.fingerprint, secret=True)
        cryptor._gpg.export_keys.assert_any_call(keys.fingerprint, secret=True)
        mock_keyfile.write.called_once_with(pubkey + seckey)

    def test_encrypt_returns_gpg_encrypted_data(self):
        cryptor = Cryptor("path/to/database")
        cryptor._import_keys = self.Mock()
        encrypted = "encrypted data"
        cryptor._gpg.encrypt.return_value = encrypted

        self.assertEqual(cryptor.encrypt("data"), str(encrypted))

    def test_decrypt_returns_gpg_decrypted_data(self):
        cryptor = Cryptor("path/to/database")
        cryptor._import_keys = self.Mock()
        decrypted = "decrypted data"
        cryptor._gpg.decrypt.return_value = decrypted

        self.assertEqual(cryptor.decrypt("data", "passphrase"), str(decrypted))

    def test_passphrase_check_raises_value_error_when_bad_passphrase(self):
        cryptor = Cryptor("path/to/database")
        cryptor._import_keys = self.Mock()
        passphrase = "passphrase"
        result = cryptor.check(passphrase)

        self.assertTrue(result)
        self.assertTrue(cryptor._gpg.sign.called)
        cryptor._gpg.sign.assert_called_once_with(
            "testing",
            default_key=cryptor.current_key,
            passphrase=passphrase
        )

    def test_passprase_check_with_ensure_raises_value_error_with_ensure(self):
        cryptor = Cryptor("path/to/database")
        cryptor._import_keys = self.Mock()
        cryptor._gpg.sign.return_value = None
        passphrase = "passphrase"

        with self.assertRaises(ValueError):
            cryptor.check(passphrase, ensure=True)
