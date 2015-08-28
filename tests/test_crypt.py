# -*- coding: utf-8 -*-
import unittest

from passpie.crypt import (
    KEY_INPUT,
    make_key_input,
    export_keys,
    create_keys
)


def test_crypt_make_key_input_handles_unicode_encode_error(mocker):
    passphrase = 's3cr3t'
    key_length = '2064'
    class ExpectedUnicodeException(UnicodeEncodeError):
        def __init__(self):
            pass

    side_effect = [
        ExpectedUnicodeException,
        KEY_INPUT.format(key_length, passphrase)
    ]
    mock_key_input = mocker.patch('passpie.crypt.KEY_INPUT', new=mocker.MagicMock())
    mock_key_input.format.side_effect = side_effect

    key_input = make_key_input(passphrase, key_length)

    assert key_input == KEY_INPUT.format(key_length, passphrase)


def test_crypt_make_key_input_handles_unicode_chars(mocker):
    passphrase = "L'éphémère"
    key_length = '2064'
    class ExpectedUnicodeException(UnicodeEncodeError):
        def __init__(self):
            pass

    side_effect = [
        ExpectedUnicodeException,
        KEY_INPUT.format(key_length, passphrase)
    ]
    mock_key_input = mocker.patch('passpie.crypt.KEY_INPUT', new=mocker.MagicMock())
    mock_key_input.format.side_effect = side_effect

    key_input = make_key_input(passphrase, key_length)

    assert key_input == KEY_INPUT.format(key_length, passphrase)


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


@unittest.skip('not implemented')
def test_create_keys_export_public_and_secret_keys_into_keyspath(mocker):
    pass
