from passpie.cli import cli
from passpie.database import CredentialFactory


def test_copy_writes_to_stdout_when_path_is_dash(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.invoke(cli, ["--passphrase", "k", "copy", "foo@bar", "-"])

    assert result.exit_code == 0, result.output
    assert result.output == "decrypted"


def test_copy_writes_to_clipboard_with_timeout_when_path_is_not(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k copy foo@bar")

    assert result.exit_code == 0, result.output
    mock_copy_to_clipboard.assert_called_once_with("decrypted", mocker.ANY)


def test_copy_exits_with_error_when_credential_not_found(irunner, mocker):
    result = irunner.run(cli, "--passphrase k copy not-a-credential")
    assert result.exit_code != 0, result.output
    assert result.output.strip() == "Error: not-a-credential not found"


def test_copy_passes_timeout_option_to_copy_to_clipboard(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    irunner.db.insert(CredentialFactory(fullname="foo@bar"))
    result = irunner.run(cli, "--passphrase k copy --timeout 5 foo@bar")

    assert result.exit_code == 0, result.output
    mock_copy_to_clipboard.assert_called_once_with(mocker.ANY, 5)
