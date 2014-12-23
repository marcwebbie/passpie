import inspect
import os
import shutil
import sys
import unittest
import gnupg
try:
    from unittest import mock
except ImportError:
    import mock

__file__ = os.path.abspath(inspect.getsourcefile(lambda _: None))

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pysswords.db import Database
from pysswords.crypt import create_key_input
from pysswords.utils import touch, which
from pysswords.credential import Credential, CredentialNotFoundError
from pysswords import __main__, crypt


def mock_create_gpg(binary, database_path, passphrase):
    gnupg_path = os.path.join(database_path, ".gnupg")
    gpg = gnupg.GPG(which(binary), homedir=gnupg_path)
    with open(os.path.join(TEST_DIR, "testkey.pub")) as f:
        gpg.import_keys(f.read())
    with open(os.path.join(TEST_DIR, "testkey.sec")) as f:
        gpg.import_keys(f.read())
    return gpg


class PysswordsTests(unittest.TestCase):

    def setUp(self):
        self.patcher_gpg = mock.patch(
            "pysswords.db.create_gpg", new=mock_create_gpg)
        self.patcher_gpg.start()

        self.database_path = os.path.join(TEST_DIR, ".pysswords")
        self.gnupg_path = os.path.join(self.database_path, ".gnupg")
        self.database = Database.create(
            path=self.database_path,
            passphrase="dummy"
        )

    def tearDown(self):
        self.patcher_gpg.stop()
        shutil.rmtree(self.database_path)

    def test(self):
        pass

    def some_credential(self, **kwargs):
        credential = Credential(
            name=kwargs.get("name", "example"),
            login=kwargs.get("login", "john"),
            password=kwargs.get("password", "my-great-password"),
            comments=kwargs.get("comments",
                                "This is login credentials for example")
        )
        return credential

    def test_init_database_creates_gnupg_hidden_directory(self):
        self.assertTrue(os.path.exists(self.database_path))
        self.assertTrue(os.path.exists(self.gnupg_path))

    def test_credentials_are_a_list_of_credential_instances(self):
        self.database.add(self.some_credential(name="John1"))
        self.database.add(self.some_credential(name="John2"))
        self.database.add(self.some_credential(name="John3"))

        for credential in self.database.credentials:
            self.assertIsInstance(credential, Credential)

    def test_add_credential_creates_directory_with_credential_name(self):
        credential = self.some_credential()
        self.database.add(credential)
        credentials = self.database.credentials
        self.assertIn(credential.name, (c.name for c in credentials))

    def test_add_credential_uses_cipher_algo_aes256_to_encrypt(self):
        fingerprint = "fingerprint"
        mock_gpg = mock.Mock()
        mock_gpg.list_keys.return_value = [{"fingerprint": fingerprint}]
        path = "path"
        database = Database(path, mock_gpg)
        credential = mock.Mock()
        database.add(credential)
        self.assertTrue(database.gpg.encrypt.called)
        args, kwargs = database.gpg.encrypt.call_args
        self.assertEqual(kwargs.get("cipher_algo"), "AES256")

    def test_save_credential_creates_dir_with_cred_name_on_given_path(self):
        credential = self.some_credential()
        credential.save(database_path=self.database_path)
        credential_path = os.path.join(self.database_path, credential.name)
        self.assertTrue(os.path.exists(credential_path))
        self.assertTrue(os.path.isdir(credential_path))

    def test_credential_method_returns_expected_credential_object(self):
        name = "email"
        login = "email@example.com"
        password = "p4ssw0rd"
        comments = "email"
        credential = Credential(
            name=name,
            login=login,
            password=password,
            comments=comments
        )
        self.database.add(credential)
        expected_credential = self.database.credential(name=name)
        self.assertEqual(expected_credential.name, name)
        self.assertEqual(expected_credential.login, login)
        self.assertEqual(expected_credential.comments, comments)

    def test_get_credential_raises_expected_exception_when_not_found(self):
        with self.assertRaises(CredentialNotFoundError):
            self.database.credential(name="None")

    def test_edit_credential_in_database_saves_new_values(self):
        credential = self.some_credential()
        self.database.add(credential)
        new_name = "new_name"
        new_login = "new_login@example.com"
        new_comments = "new comments"
        values = {
            "name": new_name,
            "login": new_login,
            "comments": new_comments,
        }
        self.database.edit(name=credential.name, values=values)
        edited_credential = self.database.credential(name=new_name)
        self.assertEqual(edited_credential.login, new_login)
        self.assertEqual(edited_credential.comments, new_comments)

    def test_list_credentials_return_credentials_from_database_dir(self):
        credential_name = "email"
        credential_path = os.path.join(self.database_path, credential_name)
        os.makedirs(credential_path)
        touch(os.path.join(credential_path, "login"))
        touch(os.path.join(credential_path, "password"))
        touch(os.path.join(credential_path, "comments"))

        credentials = self.database.credentials
        self.assertIn(credential_name, (c.name for c in credentials))

    def test_remove_credential_deletes_files_credential_dir(self):
        credential = self.some_credential()
        self.database.add(credential)
        self.assertIn(credential.name, os.listdir(self.database_path))
        self.database.remove(name=credential.name)
        self.assertNotIn(credential.name, os.listdir(self.database_path))

    def test_search_database_returns_expected_credentials(self):
        credential = self.some_credential(
            name="twitter", login="pysswords")
        credential2 = self.some_credential(
            name="wikipedia", comments="nothing")
        self.database.add(credential)
        self.database.add(credential2)

        self.assertEqual(2, len(self.database.search("wi")))
        self.assertEqual(1, len(self.database.search("twitter")))
        self.assertEqual(1, len(self.database.search("nothing")))
        self.assertEqual(1, len(self.database.search("pysswords")))
        self.assertEqual(0, len(self.database.search("unknown")))

    def test_database_from_path_method_calls_load_gpg(self):
        path = "/tmp/pysswords"
        gpg_bin = "/usr/bin/gpg"
        with mock.patch("pysswords.db.load_gpg") as mocked_load_gpg:
            Database.from_path(path, gpg_bin)
            mocked_load_gpg.assert_called_once_with(
                binary=gpg_bin,
                database_path=path
            )

    def test_database_from_path_method_returns_database_instance(self):
        path = "/tmp/pysswords"
        gpg_bin = "/usr/bin/gpg"
        with mock.patch("pysswords.db.load_gpg") as mocked_load_gpg:
            database = Database.from_path(path, gpg_bin)
            self.assertIsInstance(database, Database)

    def test_get_gpg_creates_keyrings_in_database_path(self):
        mock_create_gpg(
            binary="gpg2",
            database_path=self.database_path,
            passphrase="sup3rp4ss0rd"
        )
        self.assertIn("pubring.gpg", os.listdir(self.gnupg_path))
        self.assertIn("secring.gpg", os.listdir(self.gnupg_path))

    def test_get_gpg_return_valid_gpg_object(self):
        gpg = mock_create_gpg(
            binary="gpg2",
            database_path=self.database_path,
            passphrase="dummy"
        )
        self.assertIsInstance(gpg, gnupg.GPG)

    def test_database_key_input_returns_gpg_key_input_string(self):
        gpg = mock.Mock()
        gpg.gen_key_input = mock.Mock()
        passphrase = "dummy"
        testing = False
        create_key_input(gpg, passphrase, testing)
        gpg.gen_key_input.assert_called_once_with(
            name_real='Pysswords',
            name_email='pysswords@pysswords',
            name_comment='Autogenerated by Pysswords',
            passphrase=passphrase,
            testing=testing
        )

    def test_database_create_gpg_creates_gpg_instance(self):
        binary = "gpg2"
        database_path = "/tmp"
        passphrase = "dummy"
        gnupg_path = os.path.join(database_path, ".gnupg")
        with mock.patch("pysswords.crypt.gnupg.GPG") as mocked_GPG:
            mock_create_gpg(binary, database_path, passphrase)
            mocked_GPG.assert_called_once_with(
                which(binary),
                homedir=gnupg_path,
            )

    def test_crypt_create_gpg_generates_gpg_key(self):
        binary = "gpg"
        database_path = "/tmp/dummydb"
        passphrase = "dummypass"
        with mock.patch("pysswords.crypt.gnupg.GPG") as mocked_gpg:
            crypt.create_gpg(binary, database_path, passphrase)
            self.assertTrue(mocked_gpg().gen_key.called)

    def test_crypt_create_gpg_creates_GPG_instance(self):
        binary = "gpg"
        database_path = "/tmp/dummydb"
        gnupg_path = os.path.join(database_path, ".gnupg")
        passphrase = "dummypass"
        with mock.patch("pysswords.crypt.gnupg.GPG") as mocked_GPG:
            with mock.patch("pysswords.crypt.which") as mocked_which:
                mocked_which.return_value = "/usr/bin/gpg"
                crypt.create_gpg(binary, database_path, passphrase)
                mocked_GPG.assert_called_once_with(
                    mocked_which.return_value,
                    homedir=gnupg_path
                )

    def test_crypt_load_gpg_creates_GPG_instance(self):
        binary = "gpg"
        database_path = "/tmp/dummydb"
        gnupg_path = os.path.join(database_path, ".gnupg")
        with mock.patch("pysswords.crypt.gnupg.GPG") as mocked_GPG:
            with mock.patch("pysswords.crypt.which") as mocked_which:
                mocked_which.return_value = "/usr/bin/gpg"
                crypt.load_gpg(binary, database_path)
                mocked_GPG.assert_called_once_with(
                    mocked_which.return_value,
                    homedir=gnupg_path
                )

    def test_crypt_create_gpg_does_not_generates_gpg_key(self):
        binary = "gpg"
        database_path = "/tmp/dummydb"
        with mock.patch("pysswords.crypt.gnupg.GPG") as mocked_gpg:
            crypt.load_gpg(binary, database_path)
            self.assertFalse(mocked_gpg().gen_key.called)


class PysswordsCredentialTests(unittest.TestCase):
    def setUp(self):
        self.credential = Credential(
            name="email",
            login="john@example.com",
            password="p4ssword",
            comments="Some comments",
        )

    def tearDown(self):
        pass

    def test_credential_str_magic_methods_has_shows_name_login(self):
        self.assertIn(self.credential.name, str(self.credential))
        self.assertIn(self.credential.login, str(self.credential))


class PysswordsUtilsTests(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR + "/data")

    def tearDown(self):
        shutil.rmtree(TEST_DIR + "/data")

    def test_touch_function(self):
        touched_file = os.path.join(TEST_DIR, "data", "touched.txt")
        if sys.version_info < (3,):
            builtin_open = "__builtin__.open"
        else:
            builtin_open = "builtins.open"

        with mock.patch(builtin_open) as mocker:
            touch(touched_file)
            mocker.assert_called_once_with(touched_file, "a")

    def test_which_function_returns_expected_binary_path(self):
        python_path = which("python")
        self.assertEqual(os.path.basename(python_path), "python")

    def test_which_function_appends_exe_when_os_name_is_nt(self):
        with mock.patch("pysswords.utils.os") as mocker:
            mocker.name = "nt"
            mocker.environ = {"PATH": "/"}
            mocker.pathsep = ":"
            mocked_join = mock.Mock()
            mocker.path.join = mocked_join
            which("python")
            mocked_join.assert_any_call("/", "python.exe")


class PysswordsConsoleInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.default_database_path = os.path.join(
            os.path.expanduser("~"),
            ".pysswords"
        )
        self.mocked_passphrase = "mocked_passphrase"
        self.patcher_getpassphrase = mock.patch(
            "pysswords.__main__.getpass",
            return_value=self.mocked_passphrase)
        self.patcher_getpassphrase.start()

    def tearDown(self):
        self.patcher_getpassphrase.stop()

    def test_args_init_without_path_uses_home_user_dotpysswords(self):
        command_args = ["--init"]
        args = __main__.get_args(command_args=command_args)
        self.assertEqual(args.database, self.default_database_path)

    def test_run_with_init_args_creates_new_database(self):
        command_args = ["--init"]
        args = __main__.get_args(command_args)
        with mock.patch("pysswords.__main__.Database.create") as mocked:
            __main__.run(args)
            mocked.assert_called_once_with(
                path=self.default_database_path,
                passphrase=self.mocked_passphrase,
                gpg_bin=__main__.DEFAULT_GPG_BINARY
            )

    def test_getpassphrase_raises_value_error_when_passwords_didnt_match(self):
        if sys.version_info < (3,):
            builtin_print = "__builtin__.print"
        else:
            builtin_print = "builtins.print"
        with mock.patch(builtin_print):
            with mock.patch("pysswords.__main__.getpass") as mocked:
                mocked.side_effect = ["pass", "wrong"] * 3
                with self.assertRaises(ValueError):
                    __main__.get_password()

    def test_interface_handles_gpg_binary_argument(self):
        gpg_binary = "gpg_binary"
        command_args = ["--gpg", gpg_binary, "--init"]
        args = __main__.get_args(command_args=command_args)
        with mock.patch("pysswords.__main__.Database.create") as mocked:
            __main__.run(args)
            mocked.assert_called_once_with(
                path=self.default_database_path,
                passphrase=self.mocked_passphrase,
                gpg_bin=gpg_binary
            )

    def test_console_inteface_init_logs_path_to_database(self):
        mocked_db = mock.Mock()
        mocked_db.path = "/tmp/dummy/path"
        command_args = ["--init"]
        args = __main__.get_args(command_args=command_args)
        with mock.patch("pysswords.__main__.Database.create",
                        return_value=mocked_db):
            with mock.patch("pysswords.__main__.logging.info") as mock_log:
                __main__.run(args)
                log_message = "Database created at '{}'".format(
                    mocked_db.path
                )
                mock_log.assert_any_call(
                    log_message
                )

    def test_interface_check_passphrase_throws_error_wrong_passphrase(self):
        mocked_db = mock.Mock()
        mocked_db.gpg.sign.return_value = False
        with self.assertRaises(ValueError):
            __main__.check_passphrase(database=mocked_db, passphrase="dummy")

    def test_get_args_raise_parser_error_when_arg_clipboard_without_get(self):
        with open(os.devnull, 'w') as devnull:
            with mock.patch("sys.stderr", devnull):
                with self.assertRaises(SystemExit):
                    __main__.get_args("-c".split())


if __name__ == "__main__":
    if sys.version_info >= (3, 1):
        unittest.main(warnings="ignore")
    else:
        unittest.main()
