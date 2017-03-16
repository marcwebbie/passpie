from passpie.cli import cli
from passpie.database import CredentialFactory


def test_copy_writes_to_stdout_when_path_is_dash(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    result = irunner.run("passpie --passphrase k copy foo@bar -")

    assert result.exit_code == 0
    assert result.output == "decrypted"


def test_copy_writes_to_clipboard_with_timeout_when_path_is_not_passed(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    result = irunner.run("passpie --passphrase k copy foo@bar")

    assert result.exit_code == 0
    mock_copy_to_clipboard.assert_called_once_with("decrypted", mocker.ANY)


def test_copy_exits_with_error_when_credential_not_found(irunner):
    result = irunner.run("passpie --passphrase k copy not-a-credential")

    assert result.exit_code != 0
    assert result.output.strip() == "Error: not-a-credential not found"


def test_copy_passes_timeout_option_to_copy_to_clipboard(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    mock_copy_to_clipboard = mocker.patch("passpie.cli.copy_to_clipboard")
    result = irunner.run("passpie --passphrase k copy --timeout 5 foo@bar")

    assert result.exit_code == 0
    mock_copy_to_clipboard.assert_called_once_with(mocker.ANY, 5)


def test_copy_prompts_passphrase(irunner, mocker):
    irunner.run("passpie add foo@bar --random")
    mocker.patch("passpie.cli.prompt_passphrase", return_value="passphrase")
    mocker.patch("passpie.cli.GPG.encrypt", return_value="encrypted")
    mock_decrypt = mocker.patch("passpie.cli.GPG.decrypt", return_value="password")
    result = irunner.run(
        "passpie update foo@bar --password password --copy"
    )

    assert result.exit_code == 0
    mock_decrypt.assert_called_once_with("encrypted", "passphrase")
