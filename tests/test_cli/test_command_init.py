import os

from passpie.cli import cli
from passpie.utils import extract, yaml_load, touch, get_archive_format, mkdir


def test_init_database_creates_expected_files(irunner_empty):
    result = irunner_empty.passpie("init --passphrase pwd")
    db_path = os.path.join(irunner_empty.path, ".passpie")

    assert result.exit_code == 0
    assert len(os.listdir(db_path)) == 4
    assert ".git" in os.listdir(db_path)
    assert "credentials.yml" in os.listdir(db_path)
    assert "config.yml" in os.listdir(db_path)
    assert "keys.asc" in os.listdir(db_path)


def test_init_database_creates_with_recipient_adds_expected_recipient_to_config(irunner_empty):
    expected_config = {"RECIPIENT": "passpie@example.com"}
    result = irunner_empty.passpie("init --passphrase pwd --recipient passpie@example.com")
    db_path = os.path.join(irunner_empty.path, ".passpie")
    config_path = os.path.join(db_path, "config.yml")

    assert result.exit_code == 0
    assert "keys.asc" not in os.listdir(db_path)
    assert yaml_load(config_path) == expected_config


def test_init_exits_with_expected_error_when_database_exists(irunner_empty):
    mkdir(".passpie")
    result = irunner_empty.passpie("init --passphrase pwd")
    assert result.exit_code != 0
    assert result.output.strip() == "Error: Path '.passpie' exists [--force] to overwrite"


def test_init_with_force_ovewrite_existing_database_passpie_dot_db(irunner_empty):
    mkdir(".passpie")
    touch(os.path.join(".passpie", "test.txt"))
    result = irunner_empty.passpie("init --passphrase pwd --force")
    assert result.exit_code == 0


def test_init_with_no_git_option_file_doesnt_initialize_a_git_repo(irunner_empty):
    result = irunner_empty.passpie("init --passphrase pwd --no-git")
    db_path = os.path.join(irunner_empty.path, ".passpie")
    assert result.exit_code == 0, result.output
    assert ".git" not in os.listdir(db_path)


def test_init_with_no_passphrase_option_prompts_passphrase(irunner_empty, prompt):
    result = irunner_empty.passpie("init")
    assert result.exit_code == 0, result.output
    assert prompt.called
    prompt.assert_called_once_with(
        "Passphrase",
        hide_input=True,
        confirmation_prompt=True,
    )
