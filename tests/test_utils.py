import re
import pytest

from passpie.utils import genpass, mkdir_open, ensure_dependencies, touch


def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


def test_genpass_generates_a_password_with_length_32(mocker):
    password = genpass("\w{32}")
    assert len(password) == 32


def test_genpass_raises_value_error_when_regex_pattern_error(mocker):
    mocker.patch('passpie.utils.rstr.xeger', side_effect=re.error)
    with pytest.raises(ValueError):
        genpass("\w{32}")


def test_mkdir_open_makedirs_on_path_dirname(mocker):
    mock_os = mocker.patch("passpie.utils.os")
    mocker.patch("passpie.utils.open", mock_open(), create=True)
    path = "path/to/foo.pass"
    with mkdir_open(path, "w"):
        dirname = mock_os.path.dirname(path)
        mock_os.makedirs.assert_called_once_with(dirname)


def test_mkdir_open_handle_oserror_for_file_exist(mocker):
    mock_os = mocker.patch("passpie.utils.os")
    mocker.patch("passpie.utils.open", mock_open(), create=True)
    path = "path/to/foo.pass"

    mock_os.makedirs.side_effect = OSError(17, "File Exists")
    with mkdir_open(path, "w") as fd:
        assert fd is not None

    mock_os.makedirs.side_effect = OSError(2, "File Not Found")
    with pytest.raises(OSError):
        with mkdir_open(path, "w") as fd:
            pass


def test_ensure_dependencies_raises_runtime_when_gpg_not_installed(mocker):
    mocker.patch('passpie.utils.which', return_value=None)

    with pytest.raises(RuntimeError) as excinfo:
        ensure_dependencies()

    assert 'GnuPG not installed. https://www.gnupg.org/' == str(excinfo.value)


def test_touch_open_file_on_path(mocker):
    mock_builtin_open = mocker.patch("passpie.utils.open",
                                     mock_open(),
                                     create=True)
    path = 'path'
    touch(path)

    assert mock_builtin_open.called
    mock_builtin_open.assert_called_once_with(path, 'w')
