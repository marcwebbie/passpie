from passpie.cli import cli
from passpie.database import CredentialFactory, Database

from tinydb import Query


def test_cli_remove_all_credentials(irunner):
    irunner.run("passpie add foo@bar spam@egg foozy@bar --random")
    result = irunner.run("passpie remove --all")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert len(db) == 0


def test_cli_remove_one_credential_by_fullname(irunner, mocker):
    mock_click_confirm = mocker.patch("passpie.cli.click.confirm", return_value=True)
    irunner.run("passpie add foo@bar spam@egg --random")
    result = irunner.run("passpie remove foo@bar")
    list_result = irunner.run("passpie list")

    assert result.exit_code == 0
    assert mock_click_confirm.called is True
    assert "spam" in list_result.output
    assert "foo" not in list_result.output


def test_cli_remove_one_credential_by_fullname_with_force_wont_prompt(irunner, mocker):
    mock_click_confirm = mocker.patch("passpie.cli.click.confirm", autospec=True)
    irunner.run("passpie add foo@bar --random")
    result = irunner.run("passpie remove -f foo@bar")
    list_result = irunner.run("passpie list")

    assert result.exit_code == 0
    assert mock_click_confirm.called is False
    assert "foo" not in list_result.output


def test_cli_remove_multiple_credentials(irunner):
    irunner.run("passpie add foo@bar spam@egg guido@python --random")
    result = irunner.run("passpie remove -f foo@bar spam@egg")
    list_result = irunner.run("passpie list")

    assert result.exit_code == 0
    assert "guido" in list_result.output
    assert "foo" not in list_result.output
    assert "spam" not in list_result.output


def test_cli_remove_multiple_credentials_by_name_only(irunner):
    irunner.run("passpie add foo@bar spam@egg guido@python --random")
    result = irunner.run("passpie remove -f bar egg")
    list_result = irunner.run("passpie list")

    assert result.exit_code == 0
    assert "guido" in list_result.output
    assert "foo" not in list_result.output
    assert "spam" not in list_result.output
