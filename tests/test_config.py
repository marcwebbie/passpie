import passpie.config


def test_config_load_gets_settings_from_local_config_when_exists(mocker):
    expected_config = {
        'short_commands': True
    }
    mocker.patch('passpie.config.os.path.exists', return_value=True)
    mocker.patch('passpie.config.read_config', return_value=expected_config)

    configuration = passpie.config.load('path')
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
    mocker.patch('passpie.config.read_config', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load('path')
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
    mocker.patch('passpie.config.read_config', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load('path')
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
    mocker.patch('passpie.config.read_config', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)

    configuration = passpie.config.load('path')
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
    mocker.patch('passpie.config.read_config', return_value=local_config)
    mocker.patch('passpie.config.read_global_config', return_value=global_config)


    configuration = passpie.config.load('path',
                                        short_commands=short_commands,
                                        genpass_length=genpass_length)
    assert configuration is not None
    assert configuration['genpass_length'] == genpass_length
    assert configuration['short_commands'] == short_commands
