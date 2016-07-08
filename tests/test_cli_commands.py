import logging
import os
import tarfile
import tempfile

import click
import pytest
import yaml

from passpie.cli import cli, find_source_format


def test_cli_verbose_sets_level_debug_when_true(irunner_with_db, mocker):
    """passpie --verbose list
    """
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner_with_db.invoke(cli, ["--verbose", "list"])
    assert result.exit_code == 0, result.output
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.INFO


def test_cli_verbose_sets_level_critical_when_false(irunner_with_db, mocker):
    """passpie list
    """
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner_with_db.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is False


def test_cli_debug_sets_level_debug_when_debug_set(irunner_with_db, mocker):
    """PASSPIE_VERBOSE=true passpie list
    """
    environ_variables = {"PASSPIE_DEBUG": "true"}
    mocker.patch.dict("passpie.cli.os.environ", environ_variables)
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner_with_db.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.DEBUG


def test_cli_verbose_sets_level_info_when_verbose_environ_variable_set(irunner_with_db, mocker):
    """PASSPIE_VERBOSE=true passpie list
    """
    environ_variables = {"PASSPIE_VERBOSE": "true"}
    mocker.patch.dict("passpie.cli.os.environ", environ_variables)
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner_with_db.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.INFO


def test_cli_init_creates_passpie_db_file(irunner):
    """passpie --passphrase p init
    """
    result = irunner.invoke(cli, ["--passphrase", "p", "init"])
    assert "passpie.db" in os.listdir(os.curdir)
    assert result.exit_code == 0


def test_cli_init_creates_passpie_db_file_with_expected_files(irunner):
    """passpie --passphrase p init
    """
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


def test_cli_init_raise_error_when_passpie_db_exists(irunner):
    """passpie --passphrase p init
    """
    with open("passpie.db", "w"):
        pass
    result = irunner.invoke(cli, ["--passphrase", "p", "init"])
    assert result.exit_code == 1
    assert result.output == u"Error: Path 'passpie.db' exists [--force] to overwrite\n"


def test_cli_init_overrides_database_when_passpie_db_exists_and_force_is_passed(irunner):
    """passpie --passphrase p init --force
    """
    with open("passpie.db", "w"):
        pass
    result = irunner.invoke(cli, ["--passphrase", "p", "init", "--force"])
    assert result.exit_code == 0


def test_cli_init_add_recipient_to_config_if_is_passed(irunner):
    """passpie --passphrase p init --recipient jdoe@example.com
    """
    result = irunner.invoke(cli, [
        "--passphrase", "p", "init", "--recipient", "jdoe@example.com"])
    assert result.exit_code == 0
    tempdir = tempfile.mkdtemp()
    with tarfile.open("passpie.db") as tf:
        tf.extractall(tempdir)
    with open(os.path.join(tempdir, "config.yml")) as f:
        config_dict = yaml.load(f.read())
    assert config_dict["RECIPIENT"] == "jdoe@example.com"


def test_cli_init_dont_create_git_repo_if_no_git_is_passed(irunner):
    """passpie --passphrase p init --no-git
    """
    result = irunner.invoke(cli, ["--passphrase", "p", "init", "--no-git"])
    assert result.exit_code == 0, result.output
    with tarfile.open("passpie.db") as tf:
        assert "./.git" not in tf.getnames()


def test_cli_init_dont_create_git_repo_when_config_git_is_false(irunner, mocker, config):
    """passpie --passphrase p init
    """
    config["GIT"] = False
    result = irunner.invoke(cli, ["--passphrase", "p", "init"])
    assert result.exit_code == 0, result.output
    with tarfile.open("passpie.db") as tf:
        assert "./.git" not in tf.getnames()


def test_cli_init_create_git_repo_when_config_git_is_true(irunner, mocker, config):
    """passpie --passphrase p init
    """
    config["GIT"] = True
    result = irunner.invoke(cli, ["--passphrase", "p", "init"])
    assert result.exit_code == 0, result.output
    with tarfile.open("passpie.db") as tf:
        assert "./.git" in tf.getnames()


def test_cli_init_create_database_in_format_dir(irunner, mocker):
    """passpie --passphrase p init database_dir --force --format dir
    """
    result = irunner.invoke(
        cli, ["--passphrase", "p", "init", "--format", "dir", "database_dir"]
    )
    assert result.exit_code == 0, result.output
    assert os.path.isdir("database_dir") is True


def test_cli_init_create_database_in_format_gztar(irunner, mocker):
    """passpie --passphrase p init database.tar.gz --force --format gztar
    """
    database_filename = "database.tar.gz"
    result = irunner.invoke(
        cli, ["--passphrase", "p", "init", "--format", "gztar", database_filename]
    )
    assert result.exit_code == 0, result.output
    assert find_source_format(database_filename) == "gztar"


def test_cli_init_create_database_in_format_bztar(irunner, mocker):
    """passpie --passphrase p init database.tar.bz2 --force --format bztar
    """
    database_filename = "database.tar.bz2"
    result = irunner.invoke(
        cli, ["--passphrase", "p", "init", "--format", "bztar", database_filename]
    )
    assert result.exit_code == 0, result.output
    assert find_source_format(database_filename) == "bztar"


def test_cli_add_credential_with_random_password(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random
    """
    mocker.patch("passpie.cli.genpass", return_value="randompassword")
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="encryptedrandompassword")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar",  "--random"])
    credentials = irunner_with_db.db.all()
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
    credentials = irunner_with_db.db.all()
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
    credentials = irunner_with_db.db.all()

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
    credentials = irunner_with_db.db.all()

    assert result.exit_code == 0
    assert {"login": "foo", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "GPG pwd", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "GPG pwd", "comment": ""} in credentials


def test_cli_add_multiple_credentials_with_random_passwords(irunner_with_db, mocker):
    """passpie --passphrase p add foo@bar --random --comment comment
    """
    mock_encrypt = mocker.patch("passpie.cli.encrypt", return_value="GPG pwd")
    result = irunner_with_db.invoke(cli, ["add", "foo@bar", "spam@egg", "foozy@bar", "--random"])
    credentials = irunner_with_db.db.all()

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


def test_cli_config_without_arguments_prints_config(irunner_with_db, mocker, config):
    result = irunner_with_db.invoke(cli, ["config"])
    assert result.exit_code == 0
    assert irunner_with_db.db.config["DATABASE"] in result.output
    assert irunner_with_db.db.config["TABLE_FORMAT"] in result.output


def test_cli_config_with_name_and_value_arguments_sets_config(irunner_with_db, mocker):
    set_result = irunner_with_db.invoke(cli, ["config", "TABLE_FORMAT", "new_table_format"])
    result = irunner_with_db.invoke(cli, ["config","TABLE_FORMAT"])
    assert set_result.exit_code == 0
    assert result.exit_code == 0
    assert "TABLE_FORMAT: new_table_format\n" == result.output


def test_cli_config_with_name_lower_case_findsargument_prints_value(irunner_with_db, mocker):
    irunner_with_db.invoke(cli, ["config", "TABLE_FORMAT", "new_table_format"])
    result = irunner_with_db.invoke(cli, ["config", "table_format"])
    assert result.exit_code == 0
    assert "TABLE_FORMAT: new_table_format\n" == result.output


def test_cli_remove_all_credentials(irunner_with_db, mocker):
    irunner_with_db.invoke(cli, ["add", "--random", "foo@bar", "spam@egg"])
    assert irunner_with_db.db.count(all) == 2
    result = irunner_with_db.invoke(cli, ["remove", "--all"])
    assert result.exit_code == 0
    assert irunner_with_db.db.count(all) == 0


def test_cli_list_all_credentials(irunner_with_db, mocker):
    irunner_with_db.invoke(cli, ["add", "--random", "foo@bar", "spam@egg"])
    result = irunner_with_db.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "spam" in result.output


def test_cli_list_filter_credentials(irunner_with_db, mocker):
    irunner_with_db.invoke(cli, ["add", "--random", "foo@bar", "spam@egg"])
    result = irunner_with_db.invoke(cli, ["list", "foo"])
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "spam" not in result.output
