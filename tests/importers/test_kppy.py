import re

try:
    from mock import Mock, mock_open
except ImportError:
    from unittest.mock import Mock, mock_open

import py.test

from passpie.importers import kppy_importer


def test_kppy_returns_false_when_kppy_is_not_installed(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', False)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()

    res = importer.match('dummy')

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with('kppy is not installed')


def test_kppy_returns_false_when_path_to_match_is_not_a_file(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', True)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()
    mock_isfile = mocker.patch('os.path.isfile', return_value=False)
    filepath = 'dummy'

    res = importer.match(filepath)

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with(
        'Filepath "{}" is not a file'.format(filepath))

def test_kppy_returns_false_when_filepath_extension_is_not_kdb(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', True)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()
    mock_isfile = mocker.patch('os.path.isfile', return_value=True)
    filepath = 'dummy.hello'

    res = importer.match(filepath)

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with(
        'Filepath "{}" is not a Keepass database'.format(filepath))

