from passpie.cli import cli
from passpie.database import Database


def test_cli_add_credential_with_random_password_with_expected_length(irunner, mocker, config):
    """
    passpie add foo@bar --random
    """
    config["PASSWORD_RANDOM_LENGTH"] = 20
    mock_genpass = mocker.patch("passpie.cli.genpass", return_value="password")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")

    result = irunner.passpie("add foo@bar --random")
    db = Database(".passpie")

    assert result.exit_code == 0
    assert len(db.all()) == 1
    assert db.all()[0]['login'] == 'foo'
    assert db.all()[0]['name'] == 'bar'
    assert db.all()[0]['password'] == 'encrypted'
    assert db.all()[0]['comment'] == ''
    mock_genpass.assert_called_once_with(None, 20)


def test_cli_add_credential_with_password_option(irunner, mocker):
    mock_encrypt = mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    expected_credential = {
        "login": "foo",
        "name": "bar",
        "password": "encrypted",
        "comment": "",
    }

    result = irunner.passpie("add foo@bar --password password")
    db = Database(".passpie")

    assert result.exit_code == 0
    assert len(db.all()) == 1
    assert expected_credential in db.all(), credentials
    mock_encrypt.assert_called_once_with("password")


def test_cli_add_credential_with_comment_option(irunner, mocker):
    result = irunner.passpie('add --random --comment commentaire foo@bar')
    db = Database(".passpie")

    assert result.exit_code == 0
    assert len(db.all()) == 1
    assert db.all()[0]['comment'] == 'commentaire'


def test_cli_add_multiple_credentials_with_random_passwords(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")

    result = irunner.passpie("add foo@bar spam@egg foozy@bar --random")
    db = Database(".passpie")
    credentials = db.all()

    assert result.exit_code == 0
    assert len(credentials) == 3
    assert {"login": "foo", "name": "bar", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "encrypted", "comment": ""} in credentials


def test_cli_add_existing_credential_errors_asking_for_force_option(irunner, mocker):
    result_first = irunner.passpie("add foo@bar --random")
    result_second = irunner.passpie("add foo@bar --random")

    assert result_first.exit_code == 0
    assert result_second.exit_code != 0
    assert result_second.output == "Error: Credential foo@bar exists. `--force` to overwrite\n"


def test_cli_add_credential_with_no_option_prompts_password(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_prompt = mocker.patch("passpie.cli.click.prompt")

    result = irunner.passpie("add foo@bar", input="password\n")

    assert result.exit_code == 0
    assert mock_prompt.called
    mock_prompt.assert_called_once_with(
        "Password", confirmation_prompt=True, hide_input=True)
