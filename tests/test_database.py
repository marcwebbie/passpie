import pytest

from passpie.cli import (
    split_fullname,
    make_fullname,
    is_git_url,
    find_source_format,
    setup_path,
    Database,
    DatabaseInitError,
)


def test_split_fullname_raises_value_error_when_invalid_name(mocker):
    invalid_fullname = ""
    error_message = "not a valid fullname: {}".format(invalid_fullname)
    with pytest.raises(ValueError) as excinfo:
        split_fullname(invalid_fullname)
        assert "{}".format(excinfo.value) == error_message


def test_split_fullname_returns_expected_login_and_name(mocker):
    assert split_fullname("foo@example") == ("foo", "example")
    assert split_fullname("foo@example.com") == ("foo", "example.com")
    assert split_fullname("@example.com") == ("", "example.com")
    assert split_fullname("example.com") == ("", "example.com")
    assert split_fullname("foo@example.com@archive.com") == ("foo@example.com", "archive.com")


def test_make_fullname_returns_expected_fullname(mocker):
    assert make_fullname("foo", "bar") == "foo@bar"
    assert make_fullname("_", "bar") == "_@bar"
    assert make_fullname(None, "bar") == "@bar"
    assert make_fullname("", "bar") == "@bar"


def test_path_is_git_url(mocker):
    assert is_git_url('https://foo@example.com/user/repo.git') is True
    assert is_git_url('https://github.com/marcwebbie/passpiedb.git') is True
    assert is_git_url('git@github.com:marcwebbie/passpiedb.git') is True

    # Not a repo
    assert is_git_url('http://example.com') is False
    assert is_git_url('https://github.com/marcwebbie/passpiedb') is False
    assert is_git_url(None) is False
    assert is_git_url('') is False
    assert is_git_url('++++++++++++++') is False


def test_find_source_path_returns_none_when_not_path(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    mocker.patch("passpie.cli.tarfile.is_tarfile", return_value=False)
    mocker.patch("passpie.cli.zipfile.is_zipfile", return_value=False)

    assert find_source_format("path") is None


def test_find_source_path_returns_dir_when_path_is_dir(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=True)

    assert find_source_format("path") is "dir"


def test_find_source_path_returns_tar_when_path_is_uncompressed_tarfile(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    mocker.patch("passpie.cli.find_compression_type", return_value=None)
    mocker.patch("passpie.cli.tarfile.is_tarfile", return_value=True)

    assert find_source_format("path") is "tar"


def test_find_source_path_returns_gztar_when_path_is_gzipped_tarfile(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    mocker.patch("passpie.cli.find_compression_type", return_value="gz")
    mocker.patch("passpie.cli.tarfile.is_tarfile", return_value=True)

    assert find_source_format("path") is "gztar"


def test_find_source_path_returns_bztar_when_path_is_bzipped_tarfile(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    mocker.patch("passpie.cli.find_compression_type", return_value="bz2")
    mocker.patch("passpie.cli.tarfile.is_tarfile", return_value=True)

    assert find_source_format("path") is "bztar"


def test_find_source_path_returns_zip_when_path_is_zipfile(mocker):
    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    mocker.patch("passpie.cli.tarfile.is_tarfile", return_value=False)
    mocker.patch("passpie.cli.zipfile.is_zipfile", return_value=True)

    assert find_source_format("path") is "zip"


def test_find_source_path_returns_git_when_path_is_git_repo_url(mocker):
    mock_is_git_url = mocker.patch("passpie.cli.is_git_url", return_value=True)

    assert find_source_format("git@github.com:marcwebbie/passpiedb.git") == "git"
    mock_is_git_url.assert_called_once_with("git@github.com:marcwebbie/passpiedb.git")

def test_database_setup_keys_raises_error_when_homedir_is_set_but_path_is_not_a_dir(mocker):
    config = {
        "DATABASE": "path/exist",
        "HOMEDIR": "path/exist",
        "RECIPIENT": "passpie@localhost",
    }

    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    MockDatabase = mocker.patch("passpie.cli.Database", autospec=True)
    instance = MockDatabase(config=config)
    instance.config = config
    expected_error_message = "HOMEDIR is set and is not a dir: path/exist"

    with pytest.raises(DatabaseInitError) as excinfo:
        Database.setup_homedir(instance)
    assert "{}".format(excinfo.value) == expected_error_message


def test_database_setup_keys_raises_error_when_homedir_path_is_dir_and_no_keys_are_found(mocker):
    config = {
        "DATABASE": "path/exist",
        "HOMEDIR": "path/exist",
        "RECIPIENT": "passpie@localhost",
    }

    mocker.patch("passpie.cli.os.path.isdir", return_value=True)
    mocker.patch("passpie.cli.yaml_load", return_value=[])
    MockDatabase = mocker.patch("passpie.cli.Database", autospec=True)
    instance = MockDatabase(config=config)
    instance.config = config
    expected_error_message = "HOMEDIR is set and is not a dir: path/exist"

    with pytest.raises(DatabaseInitError) as excinfo:
        Database.setup_homedir(instance)
    assert "{}".format(excinfo.value) == expected_error_message


def test_database_setup__raises_error_when_recipient_is_set_but_is_not_found_in_homedir(mocker):
    config = {
        "DATABASE": "path/exist",
        "HOMEDIR": "path/exist",
        "RECIPIENT": "passpie@localhost",
    }

    mocker.patch("passpie.cli.os.path.isdir", return_value=False)
    MockDatabase = mocker.patch("passpie.cli.Database", autospec=True)
    instance = MockDatabase(config=config)
    instance.config = config
    expected_error_message = "HOMEDIR is set and is not a dir: path/exist"

    with pytest.raises(DatabaseInitError) as excinfo:
        Database.setup_homedir(instance)
    assert "{}".format(excinfo.value) == expected_error_message


def test_database_setup_keys_returns_recipient_when_is_set_and_found_in_homedir(mocker):
    config = {
        "DATABASE": "path/exist",
        "HOMEDIR": "path/exist",
        "RECIPIENT": "passpie@localhost",
    }
    mock_list_keys = mocker.patch("passpie.cli.list_keys", return_value=[config["RECIPIENT"]])
    MockDatabase = mocker.patch("passpie.cli.Database", autospec=True)
    instance = MockDatabase(config=config)
    instance.config = config
    recipient = Database.setup_recipient(instance, homedir=config["HOMEDIR"])

    assert recipient == config["RECIPIENT"]
    mock_list_keys.assert_called_once_with(config["HOMEDIR"], emails=True)

def test_setup_path_clones_url_when_source_format_is_git(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="git")
    mocker.patch("passpie.cli.has_required_database_files", return_value=True)
    mock_find_database_root = mocker.patch("passpie.cli.find_database_root")
    mock_clone = mocker.patch("passpie.cli.clone", return_value="dir_path")
    path = setup_path("path")

    mock_find_database_root.assert_called_once_with("dir_path")
    assert mock_find_database_root() == path


def test_setup_path_extracts_all_files_to_temp_dirpath_when_tarfile(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="tar")
    mocker.patch("passpie.cli.has_required_database_files", return_value=True)
    mocker.patch("passpie.cli.mkdtemp", return_value="dir_path")
    mocker.patch("passpie.cli.find_database_root")
    mock_tarfile = mocker.patch("passpie.cli.tarfile")
    path = setup_path("path")

    mock_tarfile.open().__enter__().extractall.assert_called_once_with("dir_path")


def test_setup_path_extracts_all_files_to_temp_dirpath_when_zipfile(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="zip")
    mocker.patch("passpie.cli.has_required_database_files", return_value=True)
    mocker.patch("passpie.cli.mkdtemp", return_value="dir_path")
    mocker.patch("passpie.cli.find_database_root")
    mock_zipfile = mocker.patch("passpie.cli.zipfile")
    path = setup_path("path")

    mock_zipfile.open().__enter__().extractall.assert_called_once_with("dir_path")


def test_setup_path_returns_path_when_source_format_is_dir(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="dir")
    mocker.patch("passpie.cli.has_required_database_files", return_value=True)
    mock_find_database_root = mocker.patch("passpie.cli.find_database_root")
    path = setup_path("path")

    mock_find_database_root.assert_called_once_with("path")
    assert mock_find_database_root() == path


def test_setup_path_raises_runtime_error_when_unreconized_database_format(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="unrecoginized")
    with pytest.raises(RuntimeError) as excinfo:
        path = setup_path("path/to/file")
        assert excinfo.value.message == "Unrecognized database format: path/to/file"


def test_setup_path_raises_runtime_error_when_missing_required_database_files(mocker):
    mocker.patch("passpie.cli.find_source_format", return_value="dir")
    mocker.patch("passpie.cli.has_required_database_files", return_value=False)

    with pytest.raises(RuntimeError) as excinfo:
        path = setup_path("path/to/file")
        assert excinfo.value.message == "Database is missing required files: path/to/file"
