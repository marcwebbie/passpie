import click
from click.testing import CliRunner
import pytest

from passpie.cli import cli, ensure_passphrase


@pytest.fixture
def mock_deps(mocker):
    return mocker.patch('passpie.cli.ensure_dependencies')


def test_ensure_passphrase_calls_decrypt_with_encrypted_data(mocker, mock_deps):
    mock_logging = mocker.patch('passpie.cli.logging')
    mock_encrypt = mocker.patch('passpie.cli.encrypt')
    mock_decrypt = mocker.patch('passpie.cli.decrypt', return_value='OK')
    config = {'recipient': 'recipient', 'homedir': 'homedir'}

    ensure_passphrase('passphrase', config=config)
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
        ensure_passphrase('passphrase', config=config)

    assert mock_logging.error.called
    mock_logging.error.assert_called_once_with(message_full)


def test_call_to_cli_exit_with_error_when_missing_dependencies(mocker):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.ensure_dependencies', side_effect=RuntimeError)
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code != 0


def test_cli_create_database_with_configuration(mocker, mock_deps):
    mock_database = mocker.patch('passpie.cli.Database')
    mock_config = mocker.patch('passpie.cli.config')
    mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli)

    assert mock_database.called
    mock_database.assert_called_once_with(mock_config.load())


def test_cli_sets_logging_verbose_level_to_info_when_passing_one_v(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli, ['-v'])

    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.INFO
    assert result.exit_code == 0


def test_cli_sets_logging_verbose_level_to_debug_when_passing_two_v(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli, ['-vv'])

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.DEBUG


def test_cli_sets_logging_verbose_level_to_critical_when_no_verbose_passed(mocker, mock_deps):
    mocker.patch('passpie.cli.Database')
    mocker.patch('passpie.cli.config')
    mock_logging = mocker.patch('passpie.cli.logging')

    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 0
    assert mock_logging.basicConfig.called
    _, kwargs = mock_logging.basicConfig.call_args
    assert kwargs['level'] == mock_logging.CRITICAL
