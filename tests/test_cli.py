from click.testing import CliRunner
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
import pytest
try:
    import mock
except ImportError:
    from unittest import mock

from passpie import cli
from passpie.crypt import FileExistsError


@pytest.fixture
def mock_db(mocker):
    credentials = [
        {'login': 'foo', 'name': 'bar', 'fullname': 'foo@bar',
         'password': '', 'comment': ''},
        {'login': 'foa', 'name': 'bazzy', 'fullname': 'foa@bazzy',
         'password': '', 'comment': ''},
        {'login': 'spam', 'name': 'egg', 'fullname': 'spam@egg',
         'password': '', 'comment': ''},
    ]
    database = TinyDB(storage=MemoryStorage)
    database.insert_multiple(credentials)
    MockDB = mock.MagicMock(return_value=database)
    mocker.patch('passpie.cli.Database', MockDB)
    return database


@pytest.fixture
def mock_cryptor(mocker):
    mock_cryptor = mock.MagicMock()
    mock_cryptor_context = mocker.patch("passpie.cli.Cryptor")
    mock_cryptor_context().__enter__.return_value = mock_cryptor
    return mock_cryptor


def test_cli_search_find_results_by_login_regex(mock_db):
    runner = CliRunner()
    result = runner.invoke(cli.search, ['fo[oa]'])

    assert result.exit_code == 0
    assert 'foo' in result.output
    assert 'foa' in result.output
    assert 'spam' not in result.output


def test_cli_remove_delete_credential_found_by_database(mock_db):
    runner = CliRunner()
    result = runner.invoke(cli.remove, ['foo@bar'], input='y')
    result_print = runner.invoke(cli.cli)

    assert result.exit_code == 0
    assert 'foo' not in result_print.output


def test_cli_copy_credential_password_to_database(mocker, mock_db, mock_cryptor):
    fullname = 'foo@bar'
    password = 's3cr3t'
    mocker.patch('passpie.cli.ensure_passphrase')
    mock_pyperclip = mocker.patch('passpie.cli.pyperclip')
    mock_cryptor.decrypt.return_value = password
    runner = CliRunner()
    result = runner.invoke(cli.copy, [fullname], input='passphrase')

    assert result.exit_code == 0
    assert mock_pyperclip.copy.called
    mock_pyperclip.copy.assert_called_once_with(password)


def test_cli_reset_database_overwrite_old_keys(mocker, mock_db, mock_cryptor):
    mocker.patch('passpie.cli.ensure_passphrase')
    new_passphrase = mocker.patch('passpie.cli.click.prompt')()

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code == 0
    assert mock_cryptor.create_keys.called
    mock_cryptor.create_keys.assert_called_once_with(
        new_passphrase, overwrite=True)


def test_cli_reset_database_re_encrypt_all_passwords(mocker, mock_db, mock_cryptor):
    password = 's3cr3t'
    mocker.patch('passpie.cli.ensure_passphrase')
    mocker.patch('passpie.cli.Cryptor.create_keys')
    mocker.patch('passpie.cli.click.prompt')
    mock_cryptor.decrypt.return_value = password

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code is 0
    assert mock_cryptor.encrypt.call_count is len(mock_db.all())
    assert mock_cryptor.decrypt.call_count is len(mock_db.all())
    for credential in mock_db.all():
        mock_cryptor.decrypt.assert_any_call_with(credential['password'])
    for credential in mock_db.all():
        mock_cryptor.encrypt.assert_any_call_with(password)


def test_cli_reset_purges_all_elements(mocker, mock_db, mock_cryptor):
    mocker.patch('passpie.cli.ensure_passphrase')
    mocker.patch('passpie.cli.click.prompt')
    mocker.patch.object(mock_db, 'purge')

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code is 0
    assert mock_db.purge.called


def test_init_success(mock_cryptor):
    passphrase = "PASS2pie"
    runner = CliRunner()
    result = runner.invoke(cli.init, ["--passphrase", passphrase])
    expected_msg = "Initialized database in {}\n".format(cli.config.path)

    assert result.output == expected_msg
    mock_cryptor.create_keys.assert_called_once_with(passphrase)


def test_init_prints_error_when_keys_exist(mocker, mock_cryptor):
    mock_cryptor.create_keys.side_effect = FileExistsError
    passphrase = "PASS2pie"
    path = cli.config.path
    message = 'Error: Database exists in %s. `--force` to overwrite\n' % path

    runner = CliRunner()
    result = runner.invoke(cli.init, ["--passphrase", passphrase])

    assert result.exit_code is not 0
    assert result.output == message


def test_init_has_success_when_keys_exits_and_force_is_passed(mocker, mock_cryptor):
    mock_shutil = mocker.patch('passpie.cli.shutil')
    passphrase = "PASS2pie"

    runner = CliRunner()
    result = runner.invoke(cli.init, ["--passphrase", passphrase, '--force'])

    assert result.exit_code is 0
    assert mock_shutil.rmtree.called
    mock_shutil.rmtree.assert_called_once_with(cli.config.path)


def test_copy_to_clipboard_decrypts_password_to_pass_to_pyperclip(mocker, mock_cryptor):
    mock_pyperclip = mocker.patch('passpie.cli.pyperclip')
    mocker.patch('passpie.cli.get_credential_or_abort')
    mocker.patch('passpie.cli.ensure_passphrase')
    fullname = "foo@bar"
    passphrase = "passphrase"
    mock_password = mock_cryptor.decrypt()

    runner = CliRunner()
    result = runner.invoke(cli.copy, [fullname, "--passphrase", passphrase])

    assert result.exit_code is 0
    assert result.output == "Password copied to clipboard\n"
    mock_pyperclip.copy.assert_called_once_with(mock_password)


def test_import_prints_nothing_when_no_importer_is_found(mocker, mock_cryptor):
    mocker.patch('passpie.cli.find_importer', return_value=None)

    runner = CliRunner()
    result = runner.invoke(cli.import_database, ['~/something'])

    assert result.exit_code is 0
