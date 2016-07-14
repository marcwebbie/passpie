from collections import namedtuple
import os
import shutil
import sys
import tempfile

import yaml

from passpie.importers import find_importer, BaseImporter, get_instances
from passpie.importers.default_importer import DefaultImporter, has_fields


def test_find_importer_returns_first_match_default_importer(mocker):
    mock_importer = mocker.Mock()
    mock_importer2 = mocker.Mock()
    mock_importer.match.return_value = False
    mock_importer2.match.return_value = True

    mocker.patch('passpie.importers.get_instances',
                 return_value=[mock_importer, mock_importer2])

    importer = find_importer('mockpath')

    assert importer is mock_importer2


def test_default_importer_match_passpie_exported_yaml_when_all_credentials_have_required_fiels(mocker, mock_open):
    dict_content = [
        {"login": '', "name": '', "password": '', "comment": ''},
        {"login": '', "name": '', "password": '', "comment": ''},
    ]
    mocker.patch('passpie.importers.default_importer.open', mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load', return_value=dict_content)
    result = DefaultImporter().match('filepath')
    assert result is True


def test_default_importer_doest_not_match_passpie_exported_yaml_when_credentials_havent_required_fiels(mocker, mock_open):
    dict_content = [
        {"login": '', "password": '', "comment": ''},
        {"password": '', "comment": ''},
    ]
    mocker.patch('passpie.importers.default_importer.open', mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load', return_value=dict_content)
    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_match_returns_false_when_bad_yaml(mocker, mock_open):
    mocker.patch('passpie.importers.default_importer.open',
                 mock_open(), create=True)
    mocker.patch('passpie.importers.default_importer.yaml.load',
                 side_effect=[yaml.scanner.ScannerError])

    result = DefaultImporter().match('filepath')
    assert result is False


def test_default_importer_has_fields_returns_expected_value(mocker):
    assert has_fields({}) is False
    assert has_fields({"login": "login"}) is False
    assert has_fields({"name": "name"}) is False
    assert has_fields({"password": "password"}) is False
    assert has_fields({"comment": "comment"}) is False
    assert has_fields({"login": "login", "name": "name", "comment": "comment", "password": "password"}) is True
