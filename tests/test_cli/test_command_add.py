from passpie.cli import cli


def test_cli_add_credential_with_random_password_with_expected_length(irunner, mocker, config):
    config["PASSWORD_RANDOM_LENGTH"] = 20
    mock_genpass = mocker.patch("passpie.cli.genpass", return_value="password")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    expected_credential = {
        "login": "foo",
        "name": "bar",
        "password": "encrypted",
        "comment": "",
    }

    result = irunner.invoke(cli, ["add", "foo@bar",  "--random"])
    credentials = irunner.db.all()

    assert result.exit_code == 0
    assert expected_credential in credentials, credentials
    mock_genpass.assert_called_once_with(None, 20)


def test_cli_add_credential_with_password_option(irunner, mocker):
    mock_encrypt = mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    expected_credential = {
        "login": "foo",
        "name": "bar",
        "password": "encrypted",
        "comment": "",
    }

    result = irunner.invoke(cli, ["add", "foo@bar",  "--password", "password"])
    credentials = irunner.db.all()

    assert result.exit_code == 0
    assert expected_credential in credentials, credentials
    mock_encrypt.assert_called_once_with("password")


def test_cli_add_credential_with_comment_option(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    expected_credential = {
        "login": "foo",
        "name": "bar",
        "password": "encrypted",
        "comment": "comment",
    }

    result = irunner.run(cli, "add foo@bar --random --comment comment")
    credentials = irunner.db.all()

    assert result.exit_code == 0
    assert expected_credential in credentials, credentials


def test_cli_add_multiple_credentials_with_random_passwords(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")

    result = irunner.run(cli, "add foo@bar spam@egg foozy@bar --random")
    credentials = irunner.db.all()

    assert result.exit_code == 0
    assert {"login": "foo", "name": "bar", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "encrypted", "comment": ""} in credentials


def test_cli_add_multiple_credentials_with_random_passwords(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")

    result = irunner.invoke(cli, ["add", "foo@bar", "spam@egg", "foozy@bar", "--random"])
    credentials = irunner.db.all()

    assert result.exit_code == 0
    assert {"login": "foo", "name": "bar", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "spam", "name": "egg", "password": "encrypted", "comment": ""} in credentials
    assert {"login": "foozy", "name": "bar", "password": "encrypted", "comment": ""} in credentials


def test_cli_add_existing_credential_errors_asking_for_force_option(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")

    irunner.invoke(cli, ["add", "foo@bar", "--random"])
    result = irunner.invoke(cli, ["add", "foo@bar", "--random"])

    assert result.exit_code != 0
    assert result.output == "Error: Credential foo@bar exists. `--force` to overwrite\n"


def test_cli_add_credential_with_no_option_prompts_password(irunner, mocker):
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_prompt = mocker.patch("passpie.cli.click.prompt")

    result = irunner.invoke(cli, ["add", "foo@bar"], input="password\n")

    assert result.exit_code == 0
    assert mock_prompt.called
    mock_prompt.assert_called_once_with(
        "Password", confirmation_prompt=True, hide_input=True)
