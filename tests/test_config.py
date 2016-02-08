import passpie.config
import yaml


def test_config_read_opens_path_and_load_yaml_content(mocker, mock_open):
    config_file = mocker.patch('passpie.config.open', mock_open(), create=True)
    mock_yaml = mocker.patch('passpie.config.yaml')

    passpie.config.read('path')
    assert mock_yaml.load.called
    mock_yaml.load.assert_called_once_with(config_file().__enter__().read())


def test_config_read_logs_debug_when_config_file_not_found_and_returns_empty(mocker):
    mocker.patch('passpie.config.open', side_effect=IOError, create=True)
    mock_logging = mocker.patch('passpie.config.logging')

    result = passpie.config.read('path')
    assert result == {}
    assert mock_logging.debug.called
    mock_logging.debug.assert_called_once_with('config file "path" not found')


def test_config_read_logs_error_when_config_file_malformed_found_and_returns_empty(mocker):
    mocker.patch('passpie.config.open', side_effect=yaml.scanner.ScannerError('message'),
                 create=True)
    mock_logging = mocker.patch('passpie.config.logging')

    result = passpie.config.read('path')
    assert result == {}
    assert mock_logging.error.called
    mock_logging.error.assert_called_once_with('Malformed user configuration file: message')


def test_config_create_adds_an_empty_dot_config_file_to_path_when_default_false(mocker, mock_open):
    config_file = mocker.patch('passpie.config.open', mock_open(), create=True)
    mock_yaml_dump = mocker.patch('passpie.config.yaml.dump')
    overrides = {}
    passpie.config.create('path', overrides)

    config_file().__enter__().write.assert_called_once_with(
        mock_yaml_dump(overrides, default_flow_style=False)
    )


def path_is_repo_url(mocker):
    assert is_repo_url('https://foo@example.com/user/repo.git')
    assert is_repo_url('https://github.com/marcwebbie/passpie.git')
    assert is_repo_url('git@github.com:marcwebbie/passpie.git')
    assert not is_repo_url('http://example.com')
    assert not is_repo_url(None)
    assert not is_repo_url('')
    assert not is_repo_url('++++++++++++++')
