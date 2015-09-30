import pytest

from passpie.credential import split_fullname, make_fullname


def test_split_fullname_raises_value_error_when_invalid_name(mocker):
    invalid_fullname = ""
    with pytest.raises(ValueError):
        split_fullname(invalid_fullname)


def test_split_fullname_returns_expected_login_and_name(mocker):
    assert split_fullname("foo@bar") == ("foo", "bar")
    assert split_fullname("foo@bar.com") == ("foo", "bar.com")
    assert split_fullname("@bar") == ("_", "bar")
    assert split_fullname("foo@example.com@bar") == ("foo@example.com", "bar")


def test_make_fullname_returns_expected_fullname(mocker):
    assert make_fullname("foo", "bar") == "foo@bar"
    assert make_fullname("_", "bar") == "_@bar"
    assert make_fullname(None, "bar") == "_@bar"
