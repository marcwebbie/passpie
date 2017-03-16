from passpie.utils import yaml_dump
from passpie.database import Database



def test_cli_config_without_arguments_prints_config(irunner, mocker):
    result = irunner.passpie("config")
    db = Database('.passpie')

    assert result.exit_code == 0
    assert db.cfg["DATABASE"] in result.output
    assert db.cfg["TABLE_FORMAT"] in result.output


def test_cli_config_with_name_and_value_arguments_sets_config(irunner, mocker):
    set_result = irunner.passpie("config TABLE_FORMAT new_table_format")
    result = irunner.passpie("config TABLE_FORMAT")

    assert set_result.exit_code == 0
    assert result.exit_code == 0
    assert "new_table_format\n" == result.output


def test_cli_config_with_name_lower_case_finds_argument_and_prints_value(irunner, mocker):
    irunner.passpie("config TABLE_FORMAT new_table_format")
    result = irunner.passpie("config table_format")
    assert result.exit_code == 0
    assert "new_table_format\n" == result.output
