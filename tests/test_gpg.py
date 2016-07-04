# -*- coding: utf-8 -*-
import re

import pytest

from passpie.cli import (
    KEY_INPUT,
    DEVNULL,
    make_key_input,
    export_keys,
    import_keys,
    create_keys,
    Response,
    encrypt,
    decrypt,
    get_default_recipient,
)


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


def test_crypt_export_keys_calls_gpg_command_on_export_keys(mocker, mock_run):
    mock_run.return_value.std_out = 'exported keys'
    mocker.patch('passpie.cli.which', return_value='gpg')
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
    exported_keys = export_keys(homedir)

    assert mock_run.called is True
    assert exported_keys == "exported keys"
    mock_run.assert_called_once_with(command)


def test_create_keys_export_public_and_private_keys(mocker, mock_run):
    mock_export_keys = mocker.patch('passpie.cli.export_keys',
                                    side_effect=["PUBLIC KEY", "PRIVATE KEY"])
    mock_tempdir = mocker.patch('passpie.cli.mkdtemp', return_value="homedir")

    create_keys('passphrase')
    call_to_export_public_key = (('homedir',), {})
    call_to_export_private_key = (("homedir",), {'private': True})

    assert mock_export_keys.called is True
    assert mock_export_keys.call_args_list[0] == call_to_export_public_key
    assert mock_export_keys.call_args_list[1] == call_to_export_private_key


def test_encrypt_calls_gpg_encrypt_command_with_recipient(mocker, mock_run):
    mocker.patch('passpie.cli.which', return_value='gpg')
    recipient = 'passpie@local'
    password = 's3cr3t'
    mock_run.return_value.stdout = '--GPG ENCRYPTED--'
    homedir = 'homedir'
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
    result = encrypt(password, recipient, homedir)

    assert result is not None
    assert mock_run.called
    mock_run.assert_called_once_with(command, data=password)


def test_decrypt_calls_gpg_encrypt_expected_command(mocker, mock_run):
    mocker.patch('passpie.cli.which', return_value='gpg')
    recipient = 'passpie@local'
    passphrase = 'passphrase'
    homedir = 'homedir'
    data = '--GPG ENCRYPTED--'
    mock_run.return_value.stdout = 's3cr3t'
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
    result = decrypt(data, recipient, homedir=homedir, passphrase=passphrase)

    assert result is not None
    assert mock_run.called
    mock_run.assert_called_once_with(command, data=data)


def test_default_recipient_returns_first_matched_fingerprint(mocker, mock_run):
    output = '123\n456'
    mocker.patch('passpie.cli.mkdtemp')
    mocker.patch('passpie.cli.import_keys')
    mocker.patch('passpie.cli.re.search',
                 return_value=re.match('\d+', output))
    mock_run.return_value.std_out = output

    recipient = get_default_recipient('homedir', secret=False)
    assert recipient == '123'


def test_default_recipient_calls_expected_command_when_secret_is_true(mocker, mock_run):
    mocker.patch('passpie.cli.mkdtemp')
    mocker.patch('passpie.cli.import_keys')
    mocker.patch('passpie.cli.which', return_value='gpg')
    output = "123\n456"
    mock_run.return_value.std_out = output
    recipient = get_default_recipient('homedir', secret=True)

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

    assert mock_run.called is True
    mock_run.assert_called_once_with(command)
