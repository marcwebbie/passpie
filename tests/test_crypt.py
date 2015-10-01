# -*- coding: utf-8 -*-
import re

import pytest

from passpie.crypt import (
    KEY_INPUT,
    make_key_input,
    export_keys,
    create_keys,
    GPG,
)


@pytest.fixture
def mock_call(mocker):
    return mocker.patch('passpie.crypt.process.call')


def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


def test_crypt_make_key_input_handles_unicode_encode_error_handling(mocker):
    passphrase = 'passphrase'
    key_length = '2064'
    key_input = KEY_INPUT.format(key_length, passphrase)
    assert key_input == make_key_input(passphrase, key_length)


def test_crypt_make_key_input_handles_unicode_encode_error(mocker):
    passphrase = u"L'éphémère"
    key_length = '2064'
    key_input = make_key_input(passphrase, key_length)

    assert key_input is not None


def test_crypt_export_keys_calls_gpg_command_on_export_keys(mocker):
    output = 'command output'
    mock_call = mocker.patch('passpie.crypt.process.call',
                             return_value=(output, ''))
    mocker.patch('passpie.crypt.which', return_value='gpg')
    homedir = 'mock_homedir'

    secret = False
    command = [
        'gpg',
        '--no-version',
        '--batch',
        '--homedir', homedir,
        '--export-secret-keys' if secret else '--export',
        '--armor',
        '-o', '-'
    ]
    result = export_keys(homedir)

    assert mock_call.called is True
    assert result == output
    mock_call.assert_called_once_with(command)


def test_create_keys_export_public_and_secret_keys_into_stdout(mocker):
    passphrase = "passphrase"
    homedir = "mock/homedir"
    key_input = 'some key input'
    output = '--GPG--'
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mocker.patch('passpie.crypt.make_key_input', return_value=key_input)
    mock_call = mocker.patch('passpie.crypt.process.call',
                             return_value=(output, ''))
    mock_tempdir = mocker.patch('passpie.crypt.tempdir', create=True)

    mock_tempdir().__enter__.return_value = homedir
    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--homedir', homedir,
        '--gen-key',
    ]

    result = create_keys(passphrase)

    assert result == output
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=key_input)


def test_create_keys_if_path_is_passed_create_file_homedir(mocker, mock_call):
    mock_call.return_value = ('', '')
    mock_touch = mocker.patch('passpie.crypt.touch')
    mock_rename = mocker.patch('passpie.crypt.os.rename')
    mocker.patch('passpie.crypt.export_keys',
                 side_effect=['PUBLIC', 'PRIVATE'])
    keysfile = mock_touch()
    create_keys('passphrase', 'path')

    assert keysfile.write.called
    assert mock_rename.called is True
    assert mock_rename.called is True
    keysfile.write.assert_any_call_with('PUBLIC')
    keysfile.write.assert_any_call_with('PRIVATE')


def test_encrypt_calls_gpg_encrypt_command_with_recipient(mocker, mock_call):
    recipient = 'passpie@local'
    password = 's3cr3t'
    mock_call.return_value = ('--GPG ENCRYPTED--', None)
    mocker.patch('passpie.crypt.GPG.recipient', return_value=recipient)
    mocker.patch('passpie.crypt.which', return_value='gpg')
    gpg = GPG('path', recipient)
    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--always-trust',
        '--armor',
        '--recipient', recipient,
        '--homedir', gpg.homedir,
        '--encrypt'
    ]
    result = gpg.encrypt(password)

    assert result is not None
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=password)


def test_encrypt_calls_logging_error_when_command_error_occurs(mocker, mock_call):
    recipient = 'passpie@local'
    password = 's3cr3t'
    call_error_output = 'error output'
    mock_call.return_value = ('', call_error_output)
    mocker.patch('passpie.crypt.GPG.recipient', return_value=recipient)
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mock_logging = mocker.patch('passpie.crypt.logging')
    gpg = GPG('path', recipient)
    gpg.encrypt(password)

    assert mock_logging.error.called is True
    mock_logging.error.assert_called_once_with(call_error_output)


def test_decrypt_calls_gpg_encrypt_expected_command(mocker, mock_call):
    recipient = 'passpie@local'
    passphrase = 'passphrase'
    password = '--GPG ENCRYPTED--'
    mock_call.return_value = ('s3cr3t', None)
    mocker.patch('passpie.crypt.GPG.recipient', return_value=recipient)
    mocker.patch('passpie.crypt.which', return_value='gpg')
    gpg = GPG('path', recipient)
    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--always-trust',
        '--recipient', recipient,
        '--homedir', gpg.homedir,
        '--passphrase', passphrase,
        '--emit-version',
        '-o', '-',
        '-d', '-',
    ]
    result = gpg.decrypt(password, passphrase)

    assert result is not None
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=password)


def test_decrypt_calls_logging_error_when_command_error_occurs(mocker, mock_call):
    recipient = 'passpie@local'
    passphrase = 'passphrase'
    encrypted = '--GPG ENCRYPTED--'
    call_error_output = 'error output'
    mock_call.return_value = ('', call_error_output)
    mocker.patch('passpie.crypt.GPG.recipient', return_value=recipient)
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mock_logging = mocker.patch('passpie.crypt.logging')
    gpg = GPG('path', recipient)
    gpg.decrypt(encrypted, passphrase)

    assert mock_logging.error.called is True
    mock_logging.error.assert_called_once_with(call_error_output)


def test_gpg_string_representation_has_path_and_homedir(mocker, mock_call):
    mocker.patch('passpie.crypt.which', return_value='gpg')
    gpg = GPG('path', 'recipient')

    assert gpg.path in str(gpg)
    assert gpg.homedir in str(gpg)


def test_import_keys_calls_error_on_command_error_output(mocker, mock_call):
    mock_call.return_value = ('', 'error output')
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mock_logging = mocker.patch('passpie.crypt.logging')
    gpg = GPG('path', 'recipient')
    gpg.import_keys('path/to/.keys')

    assert mock_logging.error.called
    mock_logging.error.assert_called_once_with('error output')


def test_recipient_returns_recipient_if_when_recipient_is_set(mocker, mock_call):
    recipient = 'passpie@local'
    gpg = GPG('path', recipient=recipient)

    assert gpg.recipient() == recipient


def test_recipient_returns_default_recipient_when_recipient_not_set(mocker, mock_call):
    recipient = 'passpie@local'
    mocker.patch('passpie.crypt.GPG.default_recipient',
                 return_value=recipient)

    gpg = GPG('path')

    assert gpg.recipient() == recipient
    assert gpg.default_recipient.called


def test_gpg_enter_returns_self(mocker):
    with GPG('path') as gpg:
        assert isinstance(gpg, GPG)


def test_gpg_removes_temp_homedir_on_exit(mocker):
    rmtree = mocker.patch('passpie.crypt.shutil.rmtree')
    path = 'path/to/temp/homedir'
    with GPG(path) as gpg:
        gpg.temp_homedir = path

    assert rmtree.called
    rmtree.assert_called_once_with(path)


def test_gpg_exit_doesnt_calls_rmtree_on_temp_homedir_if_does_not_exists(mocker):
    rmtree = mocker.patch('passpie.crypt.shutil.rmtree', side_effect=OSError)
    with GPG('path') as gpg:
        gpg.temp_homedir = None

    assert rmtree.called is True


def test_default_recipient_sets_temp_homedir(mocker, mock_call):
    mocker.patch('passpie.crypt.GPG.import_keys')
    mock_tempfile = mocker.patch('passpie.crypt.tempfile')
    mock_call.return_value = ('', '')
    gpg = GPG('path')
    gpg.default_recipient(secret=False)

    assert mock_tempfile.mkdtemp.called is True
    assert gpg.temp_homedir == mock_tempfile.mkdtemp()


def test_default_recipient_logs_error_when_import_command_error(mocker, mock_call):
    mocker.patch('passpie.crypt.tempfile')
    mocker.patch('passpie.crypt.GPG.import_keys')
    mock_logging = mocker.patch('passpie.crypt.logging')
    mock_call.return_value = ('', 'error output')
    gpg = GPG('path')
    recipient = gpg.default_recipient(secret=False)

    assert mock_logging.error.called is True
    assert recipient == ''
    mock_logging.error.assert_called_once_with('error output')


def test_default_recipient_returns_first_matched_fingerprint(mocker, mock_call):
    output = '123\n456'
    mocker.patch('passpie.crypt.tempfile')
    mocker.patch('passpie.crypt.GPG.import_keys')
    mocker.patch('passpie.crypt.re.search',
                 return_value=re.match('\d+', output))
    mock_call.return_value = (output, '')
    gpg = GPG('path')
    recipient = gpg.default_recipient(secret=False)

    assert recipient == '123'


def test_default_recipient_calls_expected_command_when_secret(mocker, mock_call):
    mocker.patch('passpie.crypt.tempfile')
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mocker.patch('passpie.crypt.GPG.import_keys')
    output = "123\n456"
    mock_call.return_value = (output, '')
    gpg = GPG('path')
    recipient = gpg.default_recipient(secret=True)

    command = [
        'gpg',
        '--no-tty',
        '--list-{}-keys'.format('secret'),
        '--fingerprint',
        '--homedir', gpg.temp_homedir,
    ]

    assert mock_call.called is True
    mock_call.assert_called_once_with(command)
