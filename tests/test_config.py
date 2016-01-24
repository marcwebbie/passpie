import passpie.config
import yaml


def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


def test_config_read_opens_path_and_load_yaml_content(mocker):
    config_file = mocker.patch('passpie.config.open', mock_open(), create=True)()
    mock_yaml = mocker.patch('passpie.config.yaml')

    passpie.config.read('path')
    assert mock_yaml.load.called
    mock_yaml.load.assert_called_once_with(config_file.read())


def test_config_read_logs_debug_when_config_file_not_found_and_returns_default(mocker):
    mocker.patch('passpie.config.open', side_effect=IOError, create=True)
    mock_logging = mocker.patch('passpie.config.logging')

    result = passpie.config.read('path')
    assert result == passpie.config.DEFAULT
    assert mock_logging.debug.called
    mock_logging.debug.assert_called_once_with('config file "path" not found')


def test_config_read_logs_error_when_config_file_malformed_found_and_returns_empty(mocker):
    mocker.patch('passpie.config.open', side_effect=yaml.scanner.ScannerError, create=True)
    mock_logging = mocker.patch('passpie.config.logging')

    result = passpie.config.read('path')
    assert result == {}
    assert mock_logging.error.called
    mock_logging.error.assert_called_once_with('Malformed user configuration file: path')


def test_config_load_gets_settings_from_local_config_when_exists(mocker):
    expected_config = {
        'short_commands': True
    }
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read', return_value=expected_config)

    configuration = passpie.config.load()
    assert configuration is not None
    assert configuration['short_commands'] is expected_config['short_commands']

def test_config_load_overrides_global_config_with_local_config_vars(mocker):
    global_config = {
        'genpass_length': 16,
        'short_commands': True
    }
    local_config = {
        'genpass_length': 32
    }
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load()
    assert configuration is not None
    assert configuration['genpass_length'] == local_config['genpass_length']
    assert configuration['short_commands'] == global_config['short_commands']

def test_config_load_has_default_config_loaded(mocker):
    default_config = passpie.config.DEFAULT
    global_config = {
        'genpass_length': 16,
        'short_commands': True
    }
    local_config = {
        'genpass_length': 32
    }
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load()
    assert configuration is not None
    assert configuration['path'] == default_config['path']
    assert configuration['key_length'] == default_config['key_length']
    assert configuration['table_format'] == default_config['table_format']

def test_config_load_has_default_config_loaded(mocker):
    default_config = passpie.config.DEFAULT
    global_config = {
        'genpass_length': 16,
        'short_commands': True
    }
    local_config = {
        'genpass_length': 32
    }
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load()
    assert configuration is not None
    assert configuration['path'] == default_config['path']
    assert configuration['key_length'] == default_config['key_length']
    assert configuration['table_format'] == default_config['table_format']


def test_config_load_with_overrides_override_loaded_config(mocker):
    global_config = {
        'genpass_length': 16,
        'short_commands': True
    }
    local_config = {
        'genpass_length': 32
    }

    short_commands=False
    genpass_length=10
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    overrides = dict(short_commands=short_commands, genpass_length=genpass_length)
    configuration = passpie.config.load(**overrides)
    assert configuration is not None
    assert configuration['genpass_length'] == genpass_length
    assert configuration['short_commands'] == short_commands


def test_config_create_adds_an_empty_dot_config_file_to_path_when_default_false(mocker):
    config_file = mocker.patch('passpie.config.open', mock_open(), create=True)()
    mock_yaml_dump = mocker.patch('passpie.config.yaml.dump')
    overrides = {}
    passpie.config.create('path', overrides)

    config_file.write.assert_called_once_with(mock_yaml_dump(overrides, default_flow_style=False))
