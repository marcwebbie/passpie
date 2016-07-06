import yaml

from passpie.cli import config_create, config_load, config_default


def test_config_create_adds_an_empty_dot_config_file_to_path_when_default_false(mocker, mock_open):
    config_file = mocker.patch('passpie.cli.open', mock_open(), create=True)
    mock_yaml_dump = mocker.patch('passpie.cli.yaml_dump')
    overrides = {}
    config_create('path', overrides)

    config_file().__enter__().write.assert_called_once_with(
        mock_yaml_dump(overrides)
    )


def test_config_load_set_overrides_over_default(mocker):
    overrides = {
        "PATH": "override path",
        "PATTERN": "override pattern",
    }
    cfg = config_load(overrides=overrides)
    assert cfg["PATH"] == "override path"
    assert cfg["PATTERN"] == "override pattern"


def test_config_set_value_from_expected_environ_variables(mocker):
    environ_variables = {"PASSPIE_TABLE_FORMAT": "env-set-table-format"}
    mocker.patch.dict("passpie.cli.os.environ", environ_variables)
    cfg = config_default()
    assert cfg["TABLE_FORMAT"] == "env-set-table-format"
