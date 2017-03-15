from passpie.cli import cli


def test_cli_list_all_credentials(irunner, mocker):
    irunner.passpie("add --random foo@bar spam@egg")
    irunner.passpie("add --random spam@egg spam@egg")
    result = irunner.passpie("list")

    assert result.exit_code == 0
    assert "foo" in result.output
    assert "bar" in result.output
    assert "spam" in result.output
    assert "egg" in result.output


def test_cli_list_filter_credentials(irunner, mocker):
    irunner.passpie("add --random foo@bar spam@egg")
    irunner.passpie("add --random spam@egg spam@egg")
    result = irunner.passpie("list foo")

    assert result.exit_code == 0, result.output
    assert "foo" in result.output
    assert "spam" not in result.output
