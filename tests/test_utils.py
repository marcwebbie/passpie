import random
import re
import pytest

from passpie.cli import genpass, mkdir_open


def test_genpass_generates_a_password_with_length_32(mocker):
    password = genpass("\w{32}")
    assert len(password) == 32


def test_genpass_raises_value_error_when_regex_pattern_error(mocker):
    mocker.patch('passpie.cli.rstr.xeger', side_effect=re.error)
    with pytest.raises(ValueError):
        genpass("\w{32}")


def test_mkdir_open_makedirs_on_path_dirname(mocker, mock_open):
    mock_os = mocker.patch("passpie.cli.os")
    mocker.patch("passpie.cli.open", mock_open(), create=True)
    path = "path/to/foo.pass"
    with mkdir_open(path, "w"):
        dirname = mock_os.path.dirname(path)
        mock_os.makedirs.assert_called_once_with(dirname)


def test_mkdir_open_handle_oserror_for_file_exist(mocker, mock_open):
    mock_os = mocker.patch("passpie.cli.os")
    mocker.patch("passpie.cli.open", mock_open(), create=True)
    path = "path/to/foo.pass"

    mock_os.makedirs.side_effect = OSError(17, "File Exists")
    with mkdir_open(path, "w") as fd:
        assert fd is not None

    mock_os.makedirs.side_effect = OSError(2, "File Not Found")
    with pytest.raises(OSError):
        with mkdir_open(path, "w") as fd:
            pass
