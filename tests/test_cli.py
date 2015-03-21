from click.testing import CliRunner

from .helpers import MockerTestCase
from passpie.credential import split_fullname
from passpie.interface import cli
from passpie._compat import FileExistsError


class CLIDefaultTests(MockerTestCase):

    def setUp(self):
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_config = self.patch("passpie.interface.cli.config")
        self.mock_config.table = {}
        self.mock_config.table["headers"] = ["name", "login"]

    def test_default_command_prints_all_credentials(self):
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        self.MockDB().all.return_value = credentials

        runner = CliRunner()
        result = runner.invoke(cli.cli)

        for cred in credentials:
            self.assertIn(cred["name"], result.output)
            self.assertIn(cred["login"], result.output)

    def test_default_command_hides_config_hidden_columns(self):
        self.mock_config.table["hidden"] = ["login"]

        db = self.MockDB()
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        db.all.return_value = credentials

        runner = CliRunner()
        result = runner.invoke(cli.cli)
        # cli.cli()

        for cred in credentials:
            self.assertIn(cred["name"], result.output)
            self.assertNotIn(cred["login"], result.output)

    def test_default_colorize_columns_from_config_colors(self):
        self.mock_config.table["colors"] = {"login": "red"}
        self.mock_click = self.patch("passpie.interface.table.click")

        db = self.MockDB()
        credentials = [
            {"name": "example", "login": "foo"},
            {"name": "example", "login": "bar"},
            {"name": "example", "login": "spam"},
        ]
        db.all.return_value = credentials

        CliRunner().invoke(cli.cli, catch_exceptions=False)

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
            fullname=fullname,
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
            fullname=fullname,
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


class DatabaseCopyToClipboardTests(MockerTestCase):

    def setUp(self):
        self.mock_cryptor = self.MagicMock()
        mock_cryptor_context = self.patch("passpie.interface.cli.Cryptor")
        mock_cryptor_context().__enter__.return_value = self.mock_cryptor
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.pyperclip = self.patch("passpie.interface.cli.pyperclip")

    def test_copy_to_clipboard_decrypts_password_to_pass_to_pyperclip(self):
        fullname = "foo@bar"
        passphrase = "passphrase"
        runner = CliRunner()
        result = runner.invoke(
            cli.copy, [fullname, "--passphrase", passphrase])

        mock_password = self.mock_cryptor.decrypt()
        self.pyperclip.copy.assert_called_once_with(mock_password)
        self.assertEqual(
            result.output,
            "Password copied to clipboard\n".format(fullname))

    def test_abort_with_not_found_message_when_credential_not_found(self):
        self.MockDB().get.return_value = None
        fullname = "foo@bar"

        runner = CliRunner()
        result = runner.invoke(cli.copy, [fullname, "--passphrase", "pwd"])

        self.assertEqual(
            result.output,
            "Credential '{}' not found\nAborted!\n".format(fullname))

    def test_abort_with_wrong_passphrase_message_when_bad_passphrase(self):
        fullname = "foo@bar"
        cred = dict(
            fullname=fullname,
            name="bar",
            login="foo",
            password="encrypted",
            comment="",
        )
        self.MockDB().get.return_value = cred
        self.mock_cryptor.check.side_effect = ValueError

        runner = CliRunner()
        result = runner.invoke(cli.copy, [fullname, "--passphrase", "pwd"])

        self.assertEqual(result.output, "Wrong passphrase\nAborted!\n")


class UpdateTests(MockerTestCase):

    def setUp(self):
        self.mock_cryptor = self.MagicMock()
        mock_cryptor_context = self.patch("passpie.interface.cli.Cryptor")
        mock_cryptor_context().__enter__.return_value = self.mock_cryptor
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_datetime = self.patch("passpie.interface.cli.datetime")

    def test_abort_with_not_found_message_when_credential_not_found(self):
        self.MockDB().get.return_value = None
        fullname = "foo@bar"

        runner = CliRunner()
        result = runner.invoke(cli.update, [fullname, "--random"])

        self.assertEqual(
            result.output,
            "Credential '{}' not found\nAborted!\n".format(fullname))

    def test_has_no_confirmation_prompt_when_yes_is_passed(self):
        fullname = "foo@bar"
        cred = dict(
            fullname=fullname,
            name="bar",
            login="foo",
            password="encrypted",
            comment="",
            modified=self.mock_datetime.now()
        )
        self.MockDB().get.return_value = cred
        self.mock_click_confirm = self.patch(
            "passpie.interface.cli.click.confirm")

        runner = CliRunner()
        runner.invoke(cli.update, [fullname, "--random"])

        self.mock_click_confirm.assert_called_once_with(
            "Update credential '{}'".format(fullname), abort=True)

    def test_set_values_to_update_if_any(self):
        self.mock_where = self.patch("passpie.interface.cli.where")
        fullname = "foo@bar"
        cred = dict(
            fullname=fullname,
            name="bar",
            login="foo",
            password="encrypted",
            comment="",
            modified=self.mock_datetime.now()
        )
        values = cred.copy()
        new_login = "foozy"
        new_fullname = "{}@{}".format(new_login, values["name"])
        values["fullname"] = new_fullname
        values["login"] = new_login

        self.MockDB().get.return_value = cred

        runner = CliRunner()
        runner.invoke(cli.update, [fullname, "--login", new_login, "--yes"])

        self.MockDB().update.assert_called_once_with(
            values, self.mock_where("fullname") == fullname)

    def test_prompt_user_for_each_credential_attribute_if_none_passed(self):
        mock_click_prompt = self.patch("passpie.interface.cli.click.prompt")
        fullname = "foo@bar"
        cred = dict(
            fullname=fullname,
            name="bar",
            login="foo",
            password="encrypted",
            comment="",
        )
        self.MockDB().get.return_value = cred

        runner = CliRunner()
        runner.invoke(cli.update, [fullname, "--yes"])

        self.assertEqual(mock_click_prompt.call_count, 4)
        mock_click_prompt.assert_any_call("Name", default=cred["name"])
        mock_click_prompt.assert_any_call("Login", default=cred["login"])
        mock_click_prompt.assert_any_call("Comment", default=cred["comment"])
        mock_click_prompt.assert_any_call("Password", hide_input=True,
                                          default=cred["password"],
                                          confirmation_prompt=True,
                                          show_default=False,
                                          prompt_suffix=" [*****]: ")


class RemoveTests(MockerTestCase):

    def setUp(self):
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_where = self.patch("passpie.interface.cli.where")

    def test_remove_deletes_credential_from_database(self):
        fullname = "foo@bar"

        runner = CliRunner()
        runner.invoke(cli.remove, [fullname, "--yes"])

        self.MockDB().remove.assert_called_once_with(
            self.mock_where("fullname") == fullname)


class SearchTests(MockerTestCase):

    def setUp(self):
        self.MockDB = self.patch("passpie.interface.cli.Database")
        self.mock_where = self.patch("passpie.interface.cli.where")
        self.mock_config = self.patch("passpie.interface.cli.config")
        self.mock_config.table = dict(
            headers=("name", "login", "comment"),
            hidden=[],
            colors={},
            tablefmt="rst",
        )

    def test_search_prints_matched_credentials_from_database(self):
        regex = "f[oa]o"
        cred = dict(
            fullname="foo@bar",
            name="bar",
            login="foo",
            comment="",
        )
        cred2 = dict(
            fullname="fao@spam",
            name="spam",
            login="fao",
            comment="",
        )
        self.MockDB().search.return_value = [cred, cred2]
        runner = CliRunner()
        result = runner.invoke(cli.search, [regex])

        self.assertIn(cred["login"], result.output)
        self.assertIn(cred2["login"], result.output)
        self.MockDB().search.assert_called_once_with(
            self.mock_where("name").matches(regex) |
            self.mock_where("login").matches(regex) |
            self.mock_where("comment").matches(regex))
