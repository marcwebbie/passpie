from collections import namedtuple
try:
    from mock import Mock, mock_open
except ImportError:
    from unittest.mock import Mock, mock_open

import yaml

from passpie.importers import find_importer, BaseImporter, get_instances
from passpie.importers.default_importer import DefaultImporter
from passpie.importers.pysswords_importer import PysswordsImporter


def test_find_importer_returns_first_match_default_importer(mocker):
    mock_importer = Mock()
    mock_importer2 = Mock()
    mock_importer.match.return_value = False
    mock_importer2.match.return_value = True

    mocker.patch('passpie.importers.get_instances',
                 return_value=[mock_importer, mock_importer2])

    importer = find_importer('mockpath')

    assert importer is mock_importer2


def test_default_importer_match_passpie_exported_yaml(mocker):
    dict_content = {'handler': 'passpie', 'version': 1.0}
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is True


def test_default_importer_returns_false_when_bad_file(mocker):
    mockopen = mocker.patch(
        'passpie.importers.default_importer.open', mock_open(), create=True)()
    mockopen.read.side_effect = OSError

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_false_when_missing_version_key(mocker):
    dict_content = {'handler': 'passpie'}
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_false_when_missing_handler_key(mocker):
    dict_content = {'version': 1.0}
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_false_when_version_keys_isnt_float(mocker):
    dict_content = {'version': '1.0'}
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_returns_loaded_credentials_from_yaml_file(mocker):
    dict_content = {'credentials': {'name': 'foo', 'name': 'bar'}}
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 return_value=dict_content)

    result = DefaultImporter().handle('filepath')
    assert result is dict_content.get('credentials')


def test_default_importer_match_returns_false_when_bad_yaml(mocker):
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 side_effect=[yaml.scanner.ScannerError])

    result = DefaultImporter().match('filepath')
    assert result is False


def test_base_importer_log_calls_logging_debug_with_message(mocker):
    mock_logging = mocker.patch('passpie.importers.logging')
    importer = BaseImporter()
    message = 'test debugging'
    importer.log(message)

    assert mock_logging.debug.called is True
    mock_logging.debug.assert_called_once_with(message)


def test_get_instances_returns_instances_of_all_found_importers(mocker):
    Importer = Mock()
    Importer2 = Mock()
    Importer3 = Mock()
    mocker.patch('passpie.importers.get_all',
                 return_value=[Importer, Importer2, Importer3])

    importers = list(get_instances())
    assert len(importers) == 3
    assert Importer() in importers
    assert Importer2() in importers
    assert Importer3() in importers


def test_pysswords_returns_false_with_logging_when_not_installed(mocker):
    to_patch = 'passpie.importers.pysswords_importer.found_pysswords'
    mocker.patch(to_patch, return_value=False)
    importer = PysswordsImporter()
    importer.log = Mock()

    result = importer.match('filepath')
    assert result is False
    assert importer.log.called
    importer.log.assert_called_once_with('Pysswords is not installed')


def test_pysswords_returns_false_with_logging_when_path_not_dir(mocker):
    to_patch = 'passpie.importers.pysswords_importer.found_pysswords'
    mocker.patch(to_patch, return_value=True)
    mock_os = mocker.patch('passpie.importers.pysswords_importer.os')
    mock_os.path.is_dir.return_value = False
    importer = PysswordsImporter()
    importer.log = Mock()

    result = importer.match('filepath')
    assert result is False
    assert importer.log.called
    importer.log.assert_called_once_with('.keys not found in path')


def test_pysswords_returns_false_with_logging_when_keys_not_in_path(mocker):
    to_patch = 'passpie.importers.pysswords_importer.found_pysswords'
    mocker.patch(to_patch, return_value=True)
    mock_os = mocker.patch('passpie.importers.pysswords_importer.os')
    mock_os.path.is_dir.return_value = True
    mock_os.listdir.return_value = []
    importer = PysswordsImporter()
    importer.log = Mock()

    result = importer.match('filepath')
    assert result is False
    assert importer.log.called
    importer.log.assert_called_once_with('.keys not found in path')


def test_pysswords_match_returns_true_when_expected_path(mocker):
    to_patch = 'passpie.importers.pysswords_importer.found_pysswords'
    mocker.patch(to_patch, return_value=True)
    mock_os = mocker.patch('passpie.importers.pysswords_importer.os')
    mock_os.path.is_dir.return_value = True
    mock_os.listdir.return_value = ['.keys']
    importer = PysswordsImporter()

    result = importer.match('filepath')
    assert result is True


def test_pysswords_handle_returns_empty_when_bad_passphrase(mocker):
    mocker.patch('passpie.importers.pysswords_importer.click')
    to_patch = 'passpie.importers.pysswords_importer.Database'
    mock_pysswords_db = mocker.patch(to_patch, create=True)()
    mock_pysswords_db.check.return_value = False
    importer = PysswordsImporter()

    result = importer.handle('path')
    assert result == []


def test_pysswords_handle_returns_pysswords_credentials(mocker):
    Cred = namedtuple('Credential', 'name login password comment')
    credentials = [
        Cred('name', 'login', 'password', 'comment')
    ]
    mocker.patch('passpie.importers.pysswords_importer.click')
    mocker.patch('passpie.importers.pysswords_importer.make_fullname')
    to_patch = 'passpie.importers.pysswords_importer.Database'
    mock_pysswords_db = mocker.patch(to_patch, create=True)()
    mock_pysswords_db.check.return_value = True
    mock_pysswords_db.credentials = credentials
    importer = PysswordsImporter()

    result = importer.handle('path')
    assert credentials[0].name in [c['name'] for c in result]
