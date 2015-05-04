import tempfile
try:
    import mock
except ImportError:
    from unittest import mock

import click
from click.testing import CliRunner
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
import pytest

from passpie import cli
from passpie.crypt import FileExistsError


@pytest.fixture
def mock_cfg(mocker):
    tmpdir = tempfile.mkdtemp()
    config = cli.config
    config.path = tmpdir
    mocker.patch('passpie.cli.load_config', return_value=config)
    return config


@pytest.fixture
def mock_db(mocker, mock_cfg):
    mocker.patch('passpie.cli.ensure_is_database')
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
def mock_cryptor(mocker, mock_cfg):
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


def test_import_reencrypt_all_credential_passwords(mocker, mock_cryptor):
    password = 's3cret'
    credentials = [{'password': password}]
    mocker.patch('passpie.cli.Database')
    mock_importer = mocker.patch('passpie.cli.find_importer')()
    mock_importer.handle.return_value = credentials

    runner = CliRunner()
    result = runner.invoke(cli.import_database, ['something'])

    assert result.exit_code is 0
    assert mock_cryptor.encrypt.called is True
    mock_cryptor.encrypt.assert_called_once_with(password)


def test_search_prints_all_matched_search_credentials(mocker, mock_db):
    mock_db.search = mock.Mock(return_value=mock_db.all())
    mock_print_table = mocker.patch('passpie.cli.print_table')

    runner = CliRunner()
    result = runner.invoke(cli.search, ['pattern'])

    assert result.exit_code is 0
    mock_print_table.assert_called_once_with(mock_db.all())


def test_add_results_in_error_when_invalid_fullname(mocker, mock_db):
    mocker.patch('passpie.cli.split_fullname', side_effect=ValueError)

    runner = CliRunner()
    result = runner.invoke(cli.add, ['**bad**fullname', '--random'])

    assert result.exit_code is not 0
    assert result.output == 'Error: invalid fullname syntax\n'


def test_add_results_in_error_when_credential_already_exists(mocker, mock_db):
    message = 'Error: Credential foo@bar already exists. --force to overwrite\n'
    mocker.patch('passpie.cli.split_fullname', return_value=('foo', 'bar'))
    mock_db.get = mock.Mock(return_value=['found credential'])

    runner = CliRunner()
    result = runner.invoke(cli.add, ['foo@bar', '--random'])

    assert result.exit_code is not 0
    assert result.output == message


def test_get_credential_or_abort_sets_query_as_name(mocker, mock_db):
    credential = {'name': 'fake_name'}
    fullname = 'fullname'
    mocker.patch('passpie.cli.split_fullname', side_effect=ValueError)
    mock_where = mocker.patch('passpie.cli.where')
    mocker.patch.object(mock_db, 'get', return_value=credential)
    mocker.patch.object(mock_db, 'count', return_value=1)

    result = cli.get_credential_or_abort(mock_db, fullname)

    assert result == credential
    assert mock_db.get.called
    mock_db.get.assert_called_once_with(mock_where('name') == fullname)


def test_get_credential_or_abort_errors_on_credential_not_found(mocker, mock_db):
    mocker.patch.object(mock_db, 'get', return_value=None)

    with pytest.raises(click.ClickException) as excinfo:
        cli.get_credential_or_abort(mock_db, 'foo@bar')

    assert 'not found' in excinfo.value.message


def test_get_credential_or_abort_errors_on_multiple_credentials(mocker, mock_db):
    mocker.patch.object(mock_db, 'get', return_value=[{}])
    mocker.patch.object(mock_db, 'count', return_value=10)

    with pytest.raises(click.ClickException) as excinfo:
        cli.get_credential_or_abort(mock_db, 'foo@bar')

    assert 'Multiple matches' in excinfo.value.message
