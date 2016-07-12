from passpie.cli import cli


def test_cli_config_without_arguments_prints_config(irunner, mocker):
    result = irunner.run(cli, "config")
    config_content = yaml_dump(dict(db.config)).strip()
    assert result.exit_code == 0
    assert irunner.db.config["DATABASE"] in result.output
    assert irunner.db.config["TABLE_FORMAT"] in result.output


def test_cli_config_with_name_and_value_arguments_sets_config(irunner, mocker):
    set_result = irunner.run(cli, "config TABLE_FORMAT new_table_format")
    result = irunner.run(cli, "config TABLE_FORMAT")
    assert set_result.exit_code == 0
    assert result.exit_code == 0
    assert "new_table_format\n" == result.output


def test_cli_config_with_name_lower_case_finds_argument_and_prints_value(irunner, mocker):
    irunner.run(cli, "config TABLE_FORMAT new_table_format")
    result = irunner.run(cli, "config table_format")
    assert result.exit_code == 0
    assert "new_table_format\n" == result.output
