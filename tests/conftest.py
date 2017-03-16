from functools import partial
from tempfile import mkdtemp
import os
import shlex
import tarfile

from click.testing import CliRunner
import click
import pytest
import yaml

from passpie.cli import cli
from passpie.config import Config
from passpie.gpg import GPG
from passpie.database import Database
from passpie.utils import mkdir, safe_join, Archive, extract


MOCK_KEYPAIR = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1

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
=t+c8
-----END PGP PUBLIC KEY BLOCK-----
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1

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
rqS6OLyEr+nrIXC8aAoPCD8=
=iKUZ
-----END PGP PRIVATE KEY BLOCK-----"""


@pytest.yield_fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    yield mopen()


class CliRunnerWithDB(CliRunner):

    echo_stdin = True

    def execute(self, cmd, params, *args, **kwargs):
        kwargs.setdefault("catch_exceptions", False)
        return self.invoke(cmd, params.split(), *args, **kwargs)

    def passpie(self, params, *args, **kwargs):
        from passpie.cli import cli
        return self.execute(cli, params, *args, **kwargs)

    def run(self, params, *args, **kwargs):
        kwargs.setdefault("catch_exceptions", False)
        try:
            cmd_params = shlex.split(params)
        except UnicodeEncodeError:
            cmd_params = params.split()

        if cmd_params[0] == 'passpie':
            cmd_params = cmd_params[1:]
        return self.invoke(cli, cmd_params, *args, **kwargs)


    @property
    def path(self):
        return os.path.abspath(os.curdir)



@pytest.yield_fixture
def config(mocker):
    yield Config.DEFAULT


@pytest.yield_fixture
def prompt(mocker):
    yield mocker.patch("passpie.cli.click.prompt", return_value=MOCK_KEYPAIR)


@pytest.yield_fixture
def irunner_empty(mocker):
    mocker.patch("passpie.gpg.export_keys", return_value=MOCK_KEYPAIR)
    mocker.patch("passpie.cli.generate_keys", return_value=MOCK_KEYPAIR)
    mocker.patch("passpie.cli.GPG.ensure")
    runner = CliRunnerWithDB()
    with runner.isolated_filesystem():
        yield runner


@pytest.yield_fixture
def irunner(mocker):
    from passpie.utils import yaml_dump, touch, mkdir

    mocker.patch("passpie.gpg.export_keys", return_value=MOCK_KEYPAIR)
    mocker.patch("passpie.cli.generate_keys", return_value=MOCK_KEYPAIR)
    mocker.patch("passpie.cli.GPG.ensure")
    passphrase = "k"
    runner = CliRunnerWithDB()
    with runner.isolated_filesystem():
        runner.passpie("init --passphrase {}".format(passphrase))
        yield runner


@pytest.fixture
def mock_run(mocker):
    return mocker.patch('passpie.cli.run')


@pytest.fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


@pytest.fixture
def tempdir():
    return mkdtemp()


@pytest.fixture
def tempdir_with_git(tempdir):
    mkdir(safe_join(tempdir, ".git"))
    return tempdir
