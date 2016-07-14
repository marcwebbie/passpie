import pytest

from passpie.database import (
    split_fullname,
    make_fullname,
    Database,
    CredentialFactory,
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


def test_credential_factory_returns_expected_dictionary(mocker):
    credential = CredentialFactory()
    assert credential.get("login") is not None
    assert credential.get("name") is not None
    assert credential.get("password") is not None
    assert credential.get("comment") is not None


def test_credential_factory_splits_fullname_into_login_name(mocker):
    credential = CredentialFactory(fullname="foo@bar")
    assert credential["login"] == "foo"
    assert credential["name"] == "bar"


def test_credential_sets_fake_password(mocker):
    mock_faker = mocker.patch("passpie.database.Faker")
    credential = CredentialFactory(fullname="foo@bar")
    assert credential["password"] == mock_faker().password()
