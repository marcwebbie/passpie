import csv

import click
from click.testing import CliRunner
import pytest

from passpie import cli
from passpie.database import Database


@pytest.fixture
def mock_deps(mocker):
    from passpie.config import DEFAULT
    mocker.patch('passpie.cli.config.load', return_value=DEFAULT)
    return mocker.patch('passpie.cli.ensure_dependencies')


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


def test_ensure_passphrase_logs_error_when_decrypt_result_not_ok(mocker, mock_deps):
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
    mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.ensure_dependencies', side_effect=RuntimeError)
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli)
    assert result.exit_code != 0


def test_cli_create_database_with_configuration(mocker, mock_deps):
    mock_database = mocker.patch('passpie.cli.Database')
    mock_config = mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli)

    assert mock_database.called
    mock_database.assert_called_once_with(mock_config.load())


def test_cli_create_database_with_configuration_overriding_autopush(mocker, mock_deps):
    mock_database = mocker.patch('passpie.cli.Database')
    mock_config = mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli, ['--autopush', 'origin/master'])

    assert mock_config.load.called
    mock_config.load.assert_called_once_with(autopush=('origin', 'master'))


def test_cli_create_database_with_configuration_overriding_autopull(mocker, mock_deps):
    mock_database = mocker.patch('passpie.cli.Database')
    mock_config = mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli, ['--autopull', 'origin/master'])

    assert mock_config.load.called
    mock_config.load.assert_called_once_with(autopull=('origin', 'master'))


def test_cli_sets_logging_verbose_level_to_info_when_passing_one_v(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli, ['-v'])

    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.INFO
    assert result.exit_code == 0


def test_cli_sets_logging_verbose_level_to_debug_when_passing_two_v(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli, ['-vv'])

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.DEBUG


def test_cli_sets_logging_verbose_level_to_critical_when_no_verbose_passed(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli.cli)

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.CRITICAL


def test_cli_import_uses_csv_importer_when_cols_option_is_passed_with_cols_as_kwargs(mocker, mock_deps):
    mock_importer = mocker.patch('passpie.cli.importers.get')()
    cols = {
        'name': 0,
        'login': 1,
        'password': 2,
        'comment': 3,
    }
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner = CliRunner()
        with open('passwords.csv', 'w') as f:
            headers = ['Name', 'Login', 'Password', 'Comment']
            rows = [
                ['example.com', 'foo', 'password', 'comment'],
                ['example.com', 'foo2', 'password', 'comment'],
                ['example.com', 'foo3', 'password', 'comment'],
            ]
            csv_writer = csv.writer(f)
            csv_writer.writerow(headers)
            csv_writer.writerows(rows)
        result = runner.invoke(cli.cli, ['import', '--cols', 'name,login,password,comment', 'passwords.csv'])
    output = result.output
    exception = str(result.exception)
    mock_importer.handle.assert_called_once_with('passwords.csv', cols=cols)


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
