from collections import namedtuple
import os
import shutil
import sys
import tempfile

import yaml

from passpie.importers import find_importer, BaseImporter, get_instances
from passpie.importers.default_importer import DefaultImporter
from passpie.importers.pysswords_importer import PysswordsImporter


def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


def test_pysswords_returns_false_with_logging_when_not_installed(mocker):
    to_patch = 'passpie.importers.pysswords_importer.found_pysswords'
    mocker.patch(to_patch, return_value=False)
    importer = PysswordsImporter()
    importer.log = mocker.Mock()

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
    importer.log = mocker.Mock()

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
    importer.log = mocker.Mock()

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
