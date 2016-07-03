"""
def test_cat():
    @click.command()
    @click.argument('f', type=click.File())
    def cat(f):
        click.echo(f.read())

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hello World!')

        result = runner.invoke(cat, ['hello.txt'])
        assert result.exit_code == 0
        assert result.output == 'Hello World!\n'
"""
import os
import tarfile
import tempfile

import click
import yaml

from passpie.cli import cli


def test_cli_init_creates_passpie_db_file(irunner):
    """passpie --passphrase p init
    """
    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, ["--passphrase", "p", "init"])
        assert "passpie.db" in os.listdir(os.curdir)
        assert result.exit_code == 0


def test_cli_init_creates_passpie_db_file_with_expected_files(irunner):
    """passpie --passphrase p init
    """
    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, ["--passphrase", "p", "init"])
        tempdir = tempfile.mkdtemp()
        with tarfile.open("passpie.db") as tf:
            tf.extractall(tempdir)

        assert ".passpie" in os.listdir(tempdir)
        assert "config.yml" in os.listdir(tempdir)
        assert "keys.yml" in os.listdir(tempdir)
        with open(os.path.join(tempdir, "config.yml")) as f:
            config_dict = yaml.load(f.read())
        with open(os.path.join(tempdir, "keys.yml")) as f:
            keys_dict = yaml.load(f.read())
        assert "PUBLIC" in keys_dict
        assert "PRIVATE" in keys_dict


def test_cli_init_raise_error_when_passpie_db_exists(irunner):
    """passpie --passphrase p init
    """
    with irunner.isolated_filesystem():
        with open("passpie.db", "w"):
            pass
        result = irunner.invoke(cli, ["--passphrase", "p", "init"])
        assert result.exit_code == 1
        assert result.output == u"Error: Path 'passpie.db' exists [--force] to overwrite\n"


def test_cli_init_overrides_database_when_passpie_db_exists_and_force_is_passed(irunner):
    """passpie --passphrase p init --force
    """
    with irunner.isolated_filesystem():
        with open("passpie.db", "w"):
            pass
        result = irunner.invoke(cli, ["--passphrase", "p", "init", "--force"])
        assert result.exit_code == 0


def test_cli_init_add_recipient_to_config_if_is_passed(irunner):
    """passpie --passphrase p init --recipient jdoe@example.com
    """
    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, [
            "--passphrase", "p", "init", "--recipient", "jdoe@example.com"])
        assert result.exit_code == 0
        tempdir = tempfile.mkdtemp()
        with tarfile.open("passpie.db") as tf:
            tf.extractall(tempdir)
        with open(os.path.join(tempdir, "config.yml")) as f:
            config_dict = yaml.load(f.read())
        assert config_dict["recipient"] == "jdoe@example.com"


def test_cli_init_dont_create_git_repo_if_no_git_is_passed(irunner):
    """passpie --passphrase p init --no-git
    """
    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, ["--passphrase", "p", "init", "--no-git"])
        assert result.exit_code == 0, result.output
        with tarfile.open("passpie.db") as tf:
            assert "./.git" not in tf.getnames()


def test_cli_init_dont_create_git_repo_when_config_git_is_false(irunner, mocker):
    """passpie --passphrase p init
    """
    mocker.patch("passpie.cli.config_load", return_value={"GIT": False})

    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, ["--passphrase", "p", "init"])
        assert result.exit_code == 0, result.output
        with tarfile.open("passpie.db") as tf:
            assert "./.git" not in tf.getnames()


def test_cli_init_create_git_repo_when_config_git_is_true(irunner, mocker):
    """passpie --passphrase p init
    """
    mocker.patch("passpie.cli.config_load", return_value={"GIT": True})

    with irunner.isolated_filesystem():
        result = irunner.invoke(cli, ["--passphrase", "p", "init"])
        assert result.exit_code == 0, result.output
        with tarfile.open("passpie.db") as tf:
            assert "./.git" in tf.getnames()
