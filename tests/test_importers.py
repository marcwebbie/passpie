try:
    from mock import Mock
except ImportError:
    from unittest.mock import Mock

import yaml

from passpie.importers import find_importer
from passpie.importers.default import DefaultImporter


def test_find_importer_returns_first_match_default_importer(mocker):
    mock_importer = Mock()
    mock_importer2 = Mock()
    mock_importer.match.return_value = False
    mock_importer2.match.return_value = True

    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.get_instances',
                 return_value=[mock_importer, mock_importer2])

    importer = find_importer('mockpath')

    assert importer is mock_importer2


def test_default_importer_match_passpie_exported_yaml(mocker):
    dict_content = {'handler': 'passpie', 'version': 1.0}
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is True


def test_default_importer_returns_false_when_missing_version_key(mocker):
    dict_content = {'handler': 'passpie'}
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_false_when_missing_handler_key(mocker):
    dict_content = {'version': 1.0}
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_false_when_version_keys_isnt_float(mocker):
    dict_content = {'version': '1.0'}
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_loaded_credentials_from_yaml_file(mocker):
    dict_content = {'credentials': {'name': 'foo', 'name': 'bar'}}
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().handle('filepath')
    assert result is dict_content.get('credentials')


def test_default_importer_match_returns_false_when_bad_yaml(mocker):
    mocker.patch('passpie.importers.default.os.path.isfile', return_value=True)
    mocker.patch('passpie.importers.default.DefaultImporter._read_file')
    mocker.patch('passpie.importers.default.yaml.load',
                 side_effect=[yaml.scanner.ScannerError])

    result = DefaultImporter().match('filepath')
    assert result is False
