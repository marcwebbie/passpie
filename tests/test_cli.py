from click.testing import CliRunner
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
import pytest
try:
    import mock
except ImportError:
    from unittest import mock

from passpie import cli


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


def test_cli_copy_credential_password_to_database(mocker, mock_db):
    fullname = 'foo@bar'
    password = 's3cr3t'
    mocker.patch('passpie.cli.ensure_passphrase')
    mock_pyperclip = mocker.patch('passpie.cli.pyperclip')
    mocker.patch('passpie.cli.Cryptor.decrypt',
                 mock.Mock(return_value=password))
    runner = CliRunner()
    result = runner.invoke(cli.copy, [fullname], input='passphrase')

    assert result.exit_code == 0
    assert mock_pyperclip.copy.called
    mock_pyperclip.copy.assert_called_once_with(password)


def test_cli_reset_database_overwrite_old_keys(mocker, mock_db):
    mocker.patch('passpie.cli.ensure_passphrase')
    mock_create_keys = mocker.patch('passpie.cli.Cryptor.create_keys')
    mock_decrypt = mocker.patch('passpie.cli.Cryptor.decrypt')
    mock_decrypt.return_value = ''
    new_passphrase = mocker.patch('passpie.cli.click.prompt')()

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code == 0
    assert mock_create_keys.called
    mock_create_keys.assert_called_once_with(new_passphrase, overwrite=True)


def test_cli_reset_database_re_encrypt_all_passwords(mocker, mock_db):
    password = 's3cr3t'
    mocker.patch('passpie.cli.ensure_passphrase')
    mocker.patch('passpie.cli.Cryptor.create_keys')
    mocker.patch('passpie.cli.click.prompt')
    mock_encrypt = mocker.patch('passpie.cli.Cryptor.encrypt')
    mock_decrypt = mocker.patch('passpie.cli.Cryptor.decrypt')
    mock_decrypt.return_value = password

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code is 0
    assert mock_encrypt.call_count is len(mock_db.all())
    assert mock_decrypt.call_count is len(mock_db.all())
    for credential in mock_db.all():
        mock_decrypt.assert_any_call_with(credential['password'])
    for credential in mock_db.all():
        mock_encrypt.assert_any_call_with(password)


def test_cli_reset_purges_all_elements(mocker, mock_db):
    mocker.patch('passpie.cli.ensure_passphrase')
    mocker.patch('passpie.cli.Cryptor.create_keys')
    mocker.patch('passpie.cli.click.prompt')
    mocker.patch('passpie.cli.Cryptor.encrypt')
    mocker.patch('passpie.cli.Cryptor.decrypt')
    mocker.patch.object(mock_db, 'purge')

    runner = CliRunner()
    result = runner.invoke(cli.reset, input='passphrase')

    assert result.exit_code is 0
    assert mock_db.purge.called
