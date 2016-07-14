import random
import re
import pytest

from passpie.utils import (
    genpass,
    yaml_to_python,
    copy_to_clipboard,
    is_git_url,
    find_compression_type,
)


def test_genpass_generates_a_password_with_length_32(mocker):
    password = genpass(pattern="\w{32}")
    assert len(password) == 32


def test_genpass_raises_value_error_when_regex_pattern_error(mocker):
    mocker.patch('passpie.utils.rstr.xeger', side_effect=re.error(""))
    with pytest.raises(ValueError):
        genpass("\w{32}")


def test_when_python_3_5_use_faker_instead_of_xeger(mocker):
    mocker.patch('passpie.utils.rstr.xeger', side_effect=KeyError)
    mock_faker = mocker.patch('passpie.utils.Faker')
    mock_faker().password.return_value = "password"
    password = genpass(pattern="\w{32}")
    assert password == "password"


def test_genpass_runs_faker_when_pattern_is_none(mocker):
    mocker.patch('passpie.utils.rstr.xeger', side_effect=re.error)
    MockFaker = mocker.patch('passpie.utils.Faker', autospec=True)
    MockFaker().password.return_value = "abcdefghijklmnop"
    password = genpass(length=16)
    assert len(password) == 16
    assert MockFaker().password.called is True
    MockFaker().password.assert_called_once_with(length=16)
    assert MockFaker().password() == password


def test_yaml_to_python_returns_expected_python_object():
    assert yaml_to_python("null") == None
    assert yaml_to_python("1") == 1
    assert yaml_to_python("abcdef") == "abcdef"
    assert yaml_to_python("[1, 2, 3, 4]") == [1, 2, 3, 4]


def test_copy_to_clipboard_calls_pyperclip_with_expected_args(mocker):
    mock_pyperclip_copy = mocker.patch("passpie.utils.pyperclip.copy")
    text = "password"
    copy_to_clipboard(text, timeout=0)
    mock_pyperclip_copy.assert_called_once_with(text)


def test_copy_to_clipboard_with_timeout_prints_dots_and_sleep_in_expected_time(mocker):
    mock_pyperclip_copy = mocker.patch("passpie.utils.pyperclip.copy")
    mock_time_sleep = mocker.patch("passpie.utils.time.sleep")
    mock_sys_stdout = mocker.patch("passpie.utils.sys.stdout")
    copy_to_clipboard("text", timeout=5)
    assert mock_sys_stdout.write.call_count == 6
    assert mock_sys_stdout.flush.call_count == 5
    assert mock_time_sleep.call_count == 5
    assert mock_pyperclip_copy.call_count == 2


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


def test_find_compression_type_returns_gzip_file(mocker):
    mocker.patch("passpie.utils.gzip.GzipFile")
    mock_bz2_file = mocker.patch("passpie.utils.bz2.BZ2File")
    mock_bz2_file().__enter__().read.side_effect = IOError

    result = find_compression_type("filename")

    assert result is not None
    assert result == "gz"


def test_find_compression_type_returns_bzip_file(mocker):
    mock_gzip_file = mocker.patch("passpie.utils.gzip.GzipFile")
    mock_gzip_file().__enter__().read.side_effect = IOError
    mocker.patch("passpie.utils.bz2.BZ2File")

    result = find_compression_type("filename")

    assert result is not None
    assert result == "bz2"
