# -*- coding: utf-8 -*-
import re

import pytest

import passpie.crypt
from passpie.crypt import (
    KEY_INPUT,
    DEVNULL,
    make_key_input,
    export_keys,
    import_keys,
    create_keys,
)


@pytest.fixture
def mock_call(mocker):
    return mocker.patch('passpie.crypt.process.call')

@pytest.fixture
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
    mock_call = mocker.patch('passpie.crypt.process.call', return_value=(output, ''))
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
    mock_tempdir = mocker.patch('passpie.crypt.tempdir', return_value=homedir)

    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--homedir', homedir,
        '--gen-key',
    ]

    result = create_keys(passphrase)

    assert result == output
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=key_input)


def test_create_keys_if_path_is_passed_create_file_homedir(mocker, mock_call, mock_open):
    mock_call.return_value = ('', '')
    mock_tempdir = mocker.patch('passpie.crypt.tempdir', mock_open(), create=True)
    mocker.patch('passpie.crypt.export_keys', side_effect=['PUBLIC', 'PRIVATE'])
    mock_open = mocker.patch("passpie.crypt.open", mock_open(), create=True)
    mock_keysfile = mock_open().__enter__()
    mock_tempdir().__enter__().return_value = 'create_keys'

    create_keys('passphrase', 'path')
    assert mock_keysfile.write.called
    mock_keysfile.write.assert_any_call('PUBLIC')
    mock_keysfile.write.assert_any_call('PRIVATE')


def test_encrypt_calls_gpg_encrypt_command_with_recipient(mocker, mock_call):
    recipient = 'passpie@local'
    password = 's3cr3t'
    mock_call.return_value = ('--GPG ENCRYPTED--', None)
    homedir = 'homedir'
    mocker.patch('passpie.crypt.which', return_value='gpg')
    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--always-trust',
        '--armor',
        '--recipient', recipient,
        '--homedir', homedir,
        '--encrypt'
    ]
    result = passpie.crypt.encrypt(password, recipient, homedir)

    assert result is not None
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=password)


def test_decrypt_calls_gpg_encrypt_expected_command(mocker, mock_call):
    recipient = 'passpie@local'
    passphrase = 'passphrase'
    homedir = 'homedir'
    data = '--GPG ENCRYPTED--'
    mock_call.return_value = ('s3cr3t', None)
    mocker.patch('passpie.crypt.which', return_value='gpg')
    command = [
        'gpg',
        '--batch',
        '--no-tty',
        '--always-trust',
        '--recipient', recipient,
        '--homedir', homedir,
        '--passphrase', passphrase,
        '--emit-version',
        '-o', '-',
        '-d', '-',
    ]
    result = passpie.crypt.decrypt(data, recipient, passphrase, homedir)

    assert result is not None
    assert mock_call.called
    mock_call.assert_called_once_with(command, input=data)


def test_default_recipient_returns_first_matched_fingerprint(mocker, mock_call):
    output = '123\n456'
    mocker.patch('passpie.crypt.tempdir')
    mocker.patch('passpie.crypt.import_keys')
    mocker.patch('passpie.crypt.re.search',
                 return_value=re.match('\d+', output))
    mock_call.return_value = (output, '')

    recipient = passpie.crypt.get_default_recipient('homedir', secret=False)
    assert recipient == '123'


def test_default_recipient_calls_expected_command_when_secret(mocker, mock_call):
    mocker.patch('passpie.crypt.tempdir')
    mocker.patch('passpie.crypt.which', return_value='gpg')
    mocker.patch('passpie.crypt.import_keys')
    output = "123\n456"
    mock_call.return_value = (output, '')
    recipient = passpie.crypt.get_default_recipient('homedir', secret=True)

    command = [
        'gpg',
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--list-{}-keys'.format('secret'),
        '--fingerprint',
        '--homedir', 'homedir',
    ]

    assert mock_call.called is True
    mock_call.assert_called_once_with(command)
