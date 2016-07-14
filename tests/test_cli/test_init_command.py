import os

from passpie.cli import cli
from passpie.utils import extract, yaml_load, touch, get_archive_format


def test_init_database_creates_expected_files(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init")
    path = irunner_empty.db_extracted_path
    assert result.exit_code == 0, result.output
    assert ".git" in os.listdir(path)
    assert ".passpie" in os.listdir(path)
    assert "keys.yml" in os.listdir(path)
    assert "config.yml" in os.listdir(path)


def test_init_database_creates_with_recipient_adds_expected_recipient_to_config(irunner_empty):
    expected_config = {"RECIPIENT": "passpie@example.com"}
    result = irunner_empty.passpie("--passphrase pwd init --recipient passpie@example.com")
    path = irunner_empty.db_extracted_path
    assert result.exit_code == 0
    assert yaml_load(os.path.join(path, "config.yml")) == expected_config
    assert "keys.yml" not in os.listdir(path)


def test_init_exits_with_expected_error_when_database_exists(irunner_empty):
    touch("passpie.db")
    result = irunner_empty.passpie("--passphrase pwd init")
    assert result.exit_code != 0
    assert result.output.strip() == "Error: Path 'passpie.db' exists [--force] to overwrite"


def test_init_with_force_ovewrite_existing_database_passpie_dot_db(irunner_empty):
    touch("passpie.db")
    result = irunner_empty.passpie("--passphrase pwd init --force")
    assert result.exit_code == 0


def test_init_with_format_creates_file_with_expected_format_zip(irunner_empty):
    result_zip = irunner_empty.passpie("--passphrase pwd init --format zip")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "zip"


def test_init_with_format_creates_file_with_expected_format_tar(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init --format tar")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "tar"


def test_init_with_format_creates_file_with_expected_format_bztar(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init --format bztar")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "bztar"


def test_init_with_format_creates_file_with_expected_format_dir(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init --format dir")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "dir"


def test_init_with_format_creates_file_with_expected_format_gztar(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init --format gztar")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "gztar"


def test_init_without_creates_file_with_expected_format_gztar(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init")
    assert result.exit_code == 0
    assert get_archive_format("passpie.db") == "gztar"


def test_init_with_no_git_option_file_doesnt_initialize_a_git_repo(irunner_empty):
    result = irunner_empty.passpie("--passphrase pwd init --no-git")
    path = irunner_empty.db_extracted_path
    assert result.exit_code == 0, result.output
    assert ".git" not in os.listdir(path)
