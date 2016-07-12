from passpie.cli import cli


def test_cli_list_all_credentials(irunner, mocker):
    irunner.run(cli, "add --random foo@bar spam@egg")
    result = irunner.run(cli, "list")
    assert result.exit_code == 0
    assert result.exit_code == 0, result.output
    assert "foo" in result.output
    assert "spam" in result.output


def test_cli_list_filter_credentials(irunner, mocker):
    irunner.run(cli, "add --random foo@bar spam@egg")
    result = irunner.run(cli, "list foo")
    assert result.exit_code == 0, result.output
    assert "foo" in result.output
    assert "spam" not in result.output
