from click.testing import CliRunner

from .helpers import MockerTestCase
from passpie.credential import split_fullname
from passpie.interface import cli
from passpie._compat import FileExistsError


class CLIDefaultTests(MockerTestCase):

    def setUp(self):
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_config = self.patch("passpie.interface.cli.config")
        self.mock_config.headers = ["name", "login"]

    def test_default_command_prints_all_credentials(self):
        db = self.MockDB()
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        db.all.return_value = credentials

        runner = CliRunner()
        result = runner.invoke(cli.cli)

        for cred in credentials:
            self.assertIn(cred["name"], result.output)
            self.assertIn(cred["login"], result.output)

    def test_default_command_hides_config_hidden_columns(self):
        self.mock_config.hidden = ["login"]

        db = self.MockDB()
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        db.all.return_value = credentials

        runner = CliRunner()
        result = runner.invoke(cli.cli)

        for cred in credentials:
            self.assertIn(cred["name"], result.output)
            self.assertNotIn(cred["login"], result.output)

    def test_default_colorize_columns_from_config_colors(self):
        self.mock_config.colors = {"login": "red"}
        self.mock_click = self.patch("passpie.interface.cli.click")

        db = self.MockDB()
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        db.all.return_value = credentials

        CliRunner().invoke(cli.cli)

        for cred in credentials:
            self.mock_click.style.assert_any_call(cred["login"], "red")


class CliInitTests(MockerTestCase):

    config_path = cli.config.path
    message_success = "Initialized database in {}\n".format(config_path)
    message_error = "Database exists in {}. `--force` to overwrite\n".format(
        config_path)
    message_abort = "Aborted!\n"

    def setUp(self):
        self.mock_cryptor = self.MagicMock()
        self.mock_shutil = self.patch("passpie.interface.cli.shutil")
        mock_cryptor_context = self.patch("passpie.interface.cli.Cryptor")
        mock_cryptor_context().__enter__.return_value = self.mock_cryptor

    def test_database_initialization(self):
        passphrase = "PASS2pie"
        runner = CliRunner()
        result = runner.invoke(cli.init, ["--passphrase", passphrase])
        expected_msg = "Initialized database in {}\n".format(cli.config.path)

        self.assertEqual(result.output, expected_msg)
        self.mock_cryptor.create_keys.assert_called_once_with(passphrase)

    def test_database_initialization_prints_error_when_keys_exist(self):
        mock_rmtree = self.patch("passpie.interface.cli.shutil.rmtree")
        passphrase = "PASS2pie"

        runner = CliRunner()
        result = runner.invoke(
            cli.init, ["--passphrase", passphrase, "--force"])

        self.assertEqual(result.output, self.message_success)
        mock_rmtree.assert_called_once_with(self.config_path)

    def test_init_removes_path_and_create_keys_when_force_passed(self):
        self.mock_cryptor.create_keys.side_effect = FileExistsError
        passphrase = "PASS2pie"

        runner = CliRunner()
        result = runner.invoke(cli.init, ["--passphrase", passphrase])
        self.assertEqual(result.output,
                         self.message_error + self.message_abort)


class CLIAddTests(MockerTestCase):

    def setUp(self):
        self.mock_cryptor = self.MagicMock()
        mock_cryptor_context = self.patch("passpie.interface.cli.Cryptor")
        mock_cryptor_context().__enter__.return_value = self.mock_cryptor
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_datetime = self.patch("passpie.interface.cli.datetime")
        self.patch_object(self.MockDB(), "search", self.Mock(return_value=[]))

    def test_add_credential_by_fullname_creates_credential_and_add(self):
        fullname = "foo@example"
        login, name = split_fullname(fullname)
        password = "passFOO"
        encrypted_password = self.mock_cryptor.encrypt(password)
        db = self.MockDB()
        db.get.return_value = None
        cred = dict(
            name=name,
            login=login,
            password=encrypted_password,
            comment="",
            modified=self.mock_datetime.now()
        )

        runner = CliRunner()
        result = runner.invoke(cli.add, [fullname, "--password", password])
        db.insert.assert_called_once_with(cred)
        self.assertEqual(result.output, "")

    def test_add_credential_with_comment_option(self):
        fullname = "foo@example"
        login, name = split_fullname(fullname)
        password = "passFOO"
        comment = "a comment"
        encrypted_password = self.mock_cryptor.encrypt(password)
        db = self.MockDB()
        db.get.return_value = None
        cred = dict(
            name=name,
            login=login,
            password=encrypted_password,
            comment=comment,
            modified=self.mock_datetime.now()
        )

        runner = CliRunner()
        result = runner.invoke(
            cli.add, [fullname, "--password", password, "--comment", comment])
        db.insert.assert_called_once_with(cred)
        self.assertEqual(result.output, "")

    def test_add_credential_that_already_exists_abort(self):
        fullname = "foo@example"
        login, name = split_fullname(fullname)
        db = self.MockDB()
        db.get.return_value = {"name", name, "login", login}

        runner = CliRunner()
        result = runner.invoke(cli.add, [fullname, "--password", "pwd"])

        message_exists = "Credential {} already exists.\n".format(fullname)
        message_abort = "Aborted!\n"
        self.assertEqual(result.output, message_exists + message_abort)

    def test_add_credential_with_random_password(self):
        fullname = "foo@example"
        login, name = split_fullname(fullname)
        db = self.MockDB()
        db.get.return_value = {}

        runner = CliRunner()
        result = runner.invoke(cli.add, [fullname, "--random"])
        self.assertEqual(result.exit_code, 0)
