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
import pytest
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


def test_cli_add_credential_with_random_password(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random
    """
    mocker.patch("passpie.cli.genpass", return_value="randompassword")
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="encryptedrandompassword")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar",  "--random"])
    credentials = irunner_with_db.credentials()
    args, _ = mock_encrypt.call_args

    assert result.exit_code == 0
    assert args[0] == "randompassword"
    assert any(
        (e["login"] == "foo" and e["name"] == "bar" and e["password"] == "encryptedrandompassword")
        for e in credentials
    ), credentials


def test_cli_add_credential_with_password_option(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --password password
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="encryptedrandompassword")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar",  "--password", "password"])
    credentials = irunner_with_db.credentials()
    args, _ = mock_encrypt.call_args

    assert result.exit_code == 0
    assert args[0] == "password"
    assert any(
        (e["login"] == "foo" and e["name"] == "bar" and e["password"] == "encryptedrandompassword")
        for e in credentials
    ), credentials


def test_cli_add_credential_with_comment_option(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random --comment comment
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar",  "--random", "--comment", "comment"])
    credentials = irunner_with_db.credentials()

    assert result.exit_code == 0
    assert any(
        (e["login"] == "foo" and e["name"] == "bar" and e["comment"] == "comment")
        for e in credentials
    ), credentials


def test_cli_add_multiple_credentials_with_random_passwords(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random --comment comment
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar", "spam@egg", "foozy@bar", "--random"])
    credentials = irunner_with_db.credentials()

    assert result.exit_code == 0
    assert {"login": "foo", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials


def test_cli_add_multiple_credentials_with_random_passwords(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random --comment comment
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar", "spam@egg", "foozy@bar", "--random"])
    credentials = irunner_with_db.credentials()

    assert result.exit_code == 0
    assert {"login": "foo", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials


def test_cli_add_existing_credential_errors_asking_for_force_option(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar && passpie --passphrase p  add foo@bar
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    irunner_with_db.invoke(cli, ["add", "foo@bar", "--random"])
    result = irunner_with_db.invoke(cli, ["add", "foo@bar", "--random"])

    assert result.exit_code != 0
    assert result.output == "Error: Credential foo@bar exists. `--force` to overwrite\n"


def test_cli_add_credential_with_no_option_prompts_password(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar && passpie --passphrase p  add foo@bar
    """
    mock_prompt = mocker.patch("passpie.cli.click.prompt", return_value="pwd")
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar"], input="password\n")

    assert result.exit_code == 0
    assert mock_prompt.called
    mock_prompt.assert_called_once_with("Password", confirmation_prompt=True, hide_input=True)
