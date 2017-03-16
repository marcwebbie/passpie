from passpie.cli import cli
from passpie.database import Database


def test_update_credential_name_from_command_option(irunner):
    irunner.run("passpie add foo@bar spam@egg guido@python --random")
    result = irunner.run("passpie --passphrase k update foo@bar --name baz")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert not db.search(db.query("foo@bar"))
    assert db.search(db.query("foo@baz"))


def test_update_credential_login_from_command_option(irunner):
    irunner.run("passpie add foo@bar --random")
    result = irunner.run("passpie --passphrase k update foo@bar --login foozy")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert not db.search(db.query("foo@bar"))
    assert db.search(db.query("foozy@bar"))


def test_update_credential_comment_from_comment_option(irunner):
    irunner.run("passpie add foo@bar --random")
    result = irunner.run("passpie --passphrase k update foo@bar --comment some-comment")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert db.get(db.query("foo@bar"))["comment"] == 'some-comment'


def test_update_credential_password_from_password_option(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mock_encrypt = mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    result = irunner.run("passpie --passphrase k update foo@bar --password s3cr3t")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert db.get(db.query("foo@bar"))["password"] == "encrypted"
    mock_encrypt.assert_called_once_with("s3cr3t")


def test_update_credential_without_options_prompts_update_for_each_field(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    side_effect = ["foo", "bar", "password", ""]
    mock_prompt_update = mocker.patch("passpie.cli.prompt_update", side_effect=side_effect)
    result = irunner.run("passpie --passphrase k update foo@bar")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert mock_prompt_update.call_count == 4
    assert db.get(db.query("foo@bar"))


def test_update_credential_with_copy_call_copy_to_clipboard_with_decrypted_password(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="s3cr3t")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    irunner.run("passpie add foo@bar --random")
    db = Database('.passpie')
    result = irunner.run(
        "passpie --passphrase k update foo@bar --password s3cr3t --copy"
    )

    assert result.exit_code == 0
    mock_copy_to_clipboard.assert_called_once_with("s3cr3t", db.cfg["COPY_TIMEOUT"])


def test_update_credential_commit_changes_when_updated(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="s3cr3t")
    mock_commit = mocker.patch("passpie.database.Repo.commit")
    result = irunner.run(
        "passpie --passphrase k update foo@bar --password s3cr3t"
    )

    assert result.exit_code == 0
    mock_commit.assert_called_once_with("Update credentials 'foo@bar'")


def test_update_uses_expected_passphrase_when_passed_to_cli_in_copy(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_decrypt = mocker.patch("passpie.cli.GPG.decrypt", return_value="password")
    result = irunner.run(
        "passpie --passphrase passphrase update foo@bar --password password --copy"
    )

    assert result.exit_code == 0
    mock_decrypt.assert_called_once_with("encrypted", "passphrase")


def test_update_uses_expected_passphrase_when_passed_to_update_in_copy(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_decrypt = mocker.patch("passpie.cli.GPG.decrypt", return_value="password")
    result = irunner.run(
        "passpie update foo@bar --password password --copy --passphrase passphrase"
    )

    assert result.exit_code == 0
    mock_decrypt.assert_called_once_with("encrypted", "passphrase")


def test_update_prompts_passphrase_when_update_with_copy(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.prompt_passphrase", return_value="passphrase")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_decrypt = mocker.patch("passpie.cli.GPG.decrypt", return_value="password")
    result = irunner.run(
        "passpie update foo@bar --password password --copy"
    )

    assert result.exit_code == 0
    mock_decrypt.assert_called_once_with("encrypted", "passphrase")
