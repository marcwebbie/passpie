import csv

import click
from click.testing import CliRunner
import pytest

from passpie import cli
from passpie.database import Database


def test_ensure_passphrase_calls_decrypt_with_encrypted_data(mocker):
    mock_logging = mocker.patch('passpie.cli.logging')
    mock_encrypt = mocker.patch('passpie.cli.encrypt')
    mock_decrypt = mocker.patch('passpie.cli.decrypt', return_value='OK')
    config = {'recipient': 'recipient', 'homedir': 'homedir'}

    cli.ensure_passphrase('passphrase', config=config)
    assert mock_encrypt.called
    assert mock_decrypt.called
    mock_encrypt.assert_called_once_with('OK',
                                         recipient=config['recipient'],
                                         homedir=config['homedir'])
    mock_decrypt.assert_called_once_with(mock_encrypt.return_value,
                                         recipient=config['recipient'],
                                         passphrase='passphrase',
                                         homedir=config['homedir'])


def test_ensure_passphrase_logs_error_when_decrypt_result_not_ok(mocker):
    mock_logging = mocker.patch('passpie.cli.logging')
    mock_encrypt = mocker.patch('passpie.cli.encrypt')
    mock_decrypt = mocker.patch('passpie.cli.decrypt', return_value='NOT OK')
    config = {'recipient': 'recipient', 'homedir': 'homedir'}
    message_full = "Wrong passphrase for recipient: {} in homedir: {}".format(
        config['recipient'],
        config['homedir'],
    )

    with pytest.raises(click.ClickException):
        cli.ensure_passphrase('passphrase', config=config)

    assert mock_logging.error.called
    mock_logging.error.assert_called_once_with(message_full)


def test_call_to_cli_exit_with_error_when_missing_dependencies(mocker):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.ensure_dependencies', side_effect=RuntimeError)
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code != 0


def test_cli_instantiate_database_with_configuration(mocker, mock_config, irunner):
    mock_database = mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.logging')

    with mock_config() as configuration:
        result = irunner.invoke(cli.cli)

    output = result.output
    assert mock_database.called
    mock_database.assert_called_once_with(configuration.values)


def test_cli_sets_logging_verbose_level_to_info_when_passing_one_v(mocker, mock_config, irunner):
    mock_logging = mocker.patch('passpie.cli.logging')
    configuration = {
        'path': 'mocked',
        'headers': ['name', 'login'],
        'colors': {},
        'table_format': 'plain',
        'hidden': [],
        'hidden_string': '*******',
    }

    with mock_config(configuration):
        result = irunner.invoke(cli.cli, ['-v'])

    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.INFO
    assert result.exit_code == 0


def test_cli_sets_logging_verbose_level_to_debug_when_passing_two_v(mocker, mock_config):
    mock_logging = mocker.patch('passpie.cli.logging')

    with mock_config():
        runner = CliRunner()
        result = runner.invoke(cli.cli, ['-vv'], catch_exceptions=False)

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.DEBUG


def test_cli_sets_logging_verbose_level_to_critical_when_no_verbose_passed(mocker, mock_config):
    mock_logging = mocker.patch('passpie.cli.logging')

    with mock_config():
        runner = CliRunner()
        result = runner.invoke(cli.cli, [], catch_exceptions=False)

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.CRITICAL



def test_validate_cols_returns_dict_with_col_position(mocker):
    value = ',name,login,,password,,,comment'
    cols = {
        'name': 1,
        'login': 2,
        'password': 4,
        'comment': 7,
    }
    result = cli.validate_cols(ctx='ctx', param='param', value=value)
    assert result == cols


def test_validate_cols_returns_none_when_missing_cols(mocker):
    value_missing_name = ',login,,password,,,comment'
    value_missing_login = ',name,,password,,,comment'
    value_missing_password = ',name,login,,,,comment'
    value_missing_comment = ',name,login,,password,,,'

    with pytest.raises(click.BadParameter):
        cli.validate_cols(ctx='', param='', value=value_missing_name)
    with pytest.raises(click.BadParameter):
        cli.validate_cols(ctx='', param='', value=value_missing_login)
    with pytest.raises(click.BadParameter):
        cli.validate_cols(ctx='', param='', value=value_missing_password)

    assert cli.validate_cols(ctx='', param='', value=value_missing_comment) is not None


class CliTests(object):

    def test_cli_cli_list_credentials(self, mockie, mock_config, creds, irunner):
        credentials = creds.make(5)

        result = irunner.invoke(cli.cli, [])
        output = result.output
        assert result.exit_code == 0
        for credential in credentials:
            assert credential['name'] in output, output
            assert credential['login'] in output
            assert credential['comment'] in output


class CliAddTests(object):

    def test_add_credentials_with_random_password(self, mocker, mock_config, irunner):
        fullname = "foo@example.com"
        mock_genpass = mocker.patch('passpie.cli.genpass', return_value='random')

        with mock_config() as cfg:
            pattern = cfg['genpass_pattern']
            result = irunner.invoke(cli.cli, ['add', fullname, '--random'])

            assert result.exit_code == 0
            assert mock_genpass.called is True
            mock_genpass.assert_called_once_with(pattern=pattern)

    def test_add_credentials_with_force_rewrites_credential(self, mocker, creds, mock_config, irunner):
        credentials = creds.make(2)
        fullname = credentials[0]['fullname']
        mock_genpass = mocker.patch('passpie.cli.genpass', return_value='random')
        mock_db_add = mocker.patch('passpie.cli.Database.add')
        mocker.patch('passpie.cli.Database.credential',
                     return_value=credentials[0])

        with mock_config() as cfg:
            pattern = cfg['genpass_pattern']
            result = irunner.invoke(cli.cli, ['add', fullname, '--random', '--force'])

            assert result.exit_code == 0
            assert mock_db_add.called is True

    def test_add_credentials_with_copy_copy_to_clipboard(self, mocker, mock_config, irunner):
        mock_genpass = mocker.patch('passpie.cli.genpass', return_value='random')
        mock_copy = mocker.patch('passpie.cli.clipboard.copy')

        with mock_config() as cfg:
            pattern = cfg['genpass_pattern']
            result = irunner.invoke(cli.cli, ['add', "fullname@name", '--random', '--copy'])

            assert result.exit_code == 0
            assert mock_copy.called is True

    def test_add_credentials_with_interactive_open_cred_in_editor(self, mocker, mock_config, irunner):
        filename = 'path/to/credential.pass'
        mocker.patch('passpie.cli.Database.filename', return_value=filename)
        mock_genpass = mocker.patch('passpie.cli.genpass', return_value='random')
        mock_click_edit = mocker.patch('passpie.cli.click.edit')

        with mock_config() as cfg:
            pattern = cfg['genpass_pattern']
            result = irunner.invoke(cli.cli, ['add', "fullname@name", '--random', '--interactive'])

            assert result.exit_code == 0
            assert mock_click_edit.called is True
            mock_click_edit.assert_called_once_with(filename=filename)

class CliUpdateTests(object):

    def test_update_credentials_with_interactive_open_cred_in_editor(self, mocker, creds, mock_config, irunner):
        credentials = creds.make(2)
        fullname = credentials[0]['fullname']
        filename = 'path/to/credential.pass'
        mocker.patch('passpie.cli.Database.credential', return_value=credentials[0])
        mocker.patch('passpie.cli.Database.filename', return_value=filename)
        mock_genpass = mocker.patch('passpie.cli.genpass', return_value='random')
        mock_click_edit = mocker.patch('passpie.cli.click.edit')

        with mock_config() as cfg:
            pattern = cfg['genpass_pattern']
            result = irunner.invoke(cli.cli, ['update', fullname, '--random', '--interactive'])

            assert result.exit_code == 0
            assert mock_click_edit.called is True
            mock_click_edit.assert_called_once_with(filename=filename)
