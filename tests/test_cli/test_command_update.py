from passpie.cli import cli
from passpie.database import CredentialFactory


def test_update_credential_name_from_command_option(irunner, mocker):
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --name baz")

    assert result.exit_code == 0, result.output
    assert not irunner.db.search(irunner.db.query("foo@bar"))
    assert irunner.db.search(irunner.db.query("foo@baz"))


def test_update_credential_login_from_command_option(irunner, mocker):
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --login foozy")

    assert result.exit_code == 0, result.output
    assert not irunner.db.search(irunner.db.query("foo@bar"))
    assert irunner.db.search(irunner.db.query("foozy@bar"))


def test_update_credential_comment_from_command_option(irunner, mocker):
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --comment some-comment")

    assert result.exit_code == 0, result.output
    assert irunner.db.get(irunner.db.query("foo@bar"))["comment"] == 'some-comment'


def test_update_credential_comment_from_command_option(irunner, mocker):
    mock_encrypt = mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --password s3cr3t")

    assert result.exit_code == 0, result.output
    assert irunner.db.get(irunner.db.query("foo@bar"))["password"] == "encrypted"
    mock_encrypt.assert_called_once_with("s3cr3t")


def test_update_credential_without_options_prompts_update_for_each_field(irunner, mocker):
    credential = CredentialFactory(fullname="foo@bar")
    side_effect = [
        credential["login"],
        credential["name"],
        credential["password"],
        credential["comment"],
    ]
    mock_prompt_update = mocker.patch("passpie.cli.prompt_update", side_effect=side_effect)
    irunner.db.insert(credential)
    result = irunner.run(cli, "--passphrase k update foo@bar")

    assert result.exit_code == 0, result.output
    assert mock_prompt_update.call_count == 4
    mock_prompt_update.assert_any_call(credential, "login")
    mock_prompt_update.assert_any_call(credential, "name")
    mock_prompt_update.assert_any_call(credential, "password", hidden=True)
    mock_prompt_update.assert_any_call(credential, "comment")


def test_update_credential_with_copy_call_copy_to_clipboard_with_decrypted_password(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="s3cr3t")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --password s3cr3t --copy")

    assert result.exit_code == 0, result.output
    mock_copy_to_clipboard.assert_called_once_with("s3cr3t", irunner.db.config["COPY_TIMEOUT"])


def test_update_credential_commit_changes_when_updated(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="s3cr3t")
    mock_commit = mocker.patch("passpie.database.Repo.commit")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k update foo@bar --password s3cr3t")

    assert result.exit_code == 0, result.output
    mock_commit.assert_called_once_with("Update credentials 'foo@bar'")
