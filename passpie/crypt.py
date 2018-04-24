from tempfile import NamedTemporaryFile
import os
import re

from . import process
from .utils import tempdir
from ._compat import unicode

from passpie.utils import which


GPG_HOMEDIR = os.path.expanduser('~/.gnupg')
DEVNULL = open(os.devnull, 'w')
KEY_INPUT = u"""%echo Generating Passpie OpenPGP key
Key-Type: DSA
Key-Length: {}
Subkey-Type: ELG-E
Subkey-Length: 1024
Name-Real: Passpie
Name-Comment: Auto-generated by Passpie
Name-Email: passpie@local
Expire-Date: 0
Passphrase: {}
%commit
%echo done
"""


def ensure_keys(path):
    keys_path = os.path.join(os.path.expanduser(path), '.keys')
    if os.path.isfile(keys_path):
        return keys_path


def make_key_input(passphrase, key_length):
    passphrase = unicode(passphrase)
    key_length = unicode(key_length)
    key_input = KEY_INPUT.format(key_length, passphrase)
    return key_input


def export_keys(homedir):
    command = [
        which('gpg2') or which('gpg'),
        '--no-version',
        '--no-tty',
        '--homedir', homedir,
        '--export',
        '--armor',
        '-o', '-'
    ]
    output, error = process.call(command)
    return output


def export_secret_keys(homedir, passphrase):
    command = [
        which('gpg2') or which('gpg'),
        '--no-version',
        '--no-tty',
        '--pinentry-mode', 'loopback',
        '--passphrase-fd', '0',
        '--homedir', homedir,
        '--export-secret-keys',
        '--armor',
        '-o', '-'
    ]
    output, error = process.call(command, input=passphrase)
    if not output or error:
        # Fallback command in case that GPG version < 2.1
        # with versions lower than 2.1 it was possible to
        # export secret keys without passphrase
        fallback_command = [
            which('gpg2') or which('gpg'),
            '--no-version',
            '--no-tty',
            '--homedir', homedir,
            '--export-secret-keys',
            '--armor',
            '-o', '-'
        ]
        output, error = process.call(fallback_command)
    return output


def create_keys(passphrase, path=None, key_length=4096):
    homedir = tempdir()
    command = [
        which('gpg2') or which('gpg'),
        '--batch',
        '--no-tty',
        '--homedir', homedir,
        '--gen-key',
    ]
    key_input = make_key_input(passphrase, key_length)
    output, error = process.call(command, input=key_input)
    if path:
        with open(path, 'w') as keysfile:
            keysfile.write(export_keys(homedir))
            keysfile.write(export_secret_keys(homedir, passphrase))
    else:
        return output


def import_keys(keys_path, homedir):
    command = [
        which('gpg2') or which('gpg'),
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--homedir', homedir,
        '--import', keys_path
    ]
    output, err = process.call(command)
    return homedir


def get_default_recipient(homedir, secret=False):
    command = [
        which('gpg2') or which('gpg'),
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--list-{}-keys'.format('secret' if secret else 'public'),
        '--fingerprint',
        '--homedir', homedir,
    ]
    output, _ = process.call(command)
    for line in output.splitlines():
        try:
            mobj = re.search(r'(([0-9A-F]{4}\s*?){10})', line)
            fingerprint = mobj.group().replace(' ', '')
            return fingerprint
        except (AttributeError, IndexError):
            continue
    return ''


def encrypt(data, recipient, homedir):
    recipient = recipient if recipient else get_default_recipient(homedir)
    command = [
        which('gpg2') or which('gpg'),
        '--batch',
        '--no-tty',
        '--always-trust',
        '--armor',
        '--recipient', recipient,
        '--homedir', homedir,
        '--encrypt'
    ]
    output, _ = process.call(command, input=data)
    return output


def decrypt(data, recipient, passphrase, homedir):
    recipient = recipient if recipient else get_default_recipient(homedir)
    with NamedTemporaryFile("w", delete=False) as armored_file:
        armored_file.write(data)
        command = [
            which('gpg2') or which('gpg'),
            '--no-version',
            '--no-tty',
            '--pinentry-mode', 'loopback',
            '--passphrase-fd', '0',
            '--always-trust',
            '--homedir', homedir,
            '--armor',
            '--decrypt', armored_file.name,
        ]

    output, error = process.call(command, input=passphrase)
    if not output or error:
        # Fallback command in case that GPG version < 2.1
        # with versions lower than 2.1 it was possible to
        # decrypt armored data with passphrase as an option
        # now passphrases have to piped loopback
        command = [
            which('gpg2') or which('gpg'),
            '--batch',
            '--no-tty',
            '--always-trust',
            '--passphrase', passphrase,
            '--recipient', recipient,
            '--homedir', homedir,
            '-o', '-',
            '--decrypt', "-",
        ]
        output, error = process.call(command, input=data)
    return output
