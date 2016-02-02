import pytest

from passpie.importers.csv_importer import CSVImporter


def test_csv_importer_match_always_returns_false():
    importer = CSVImporter()
    assert importer.match('filepath') is False
    assert importer.match('') is False
    assert importer.match('~') is False


def test_csv_importer_with_empty_reader_raises_value_error(mocker, mock_open):
    mocker.patch('passpie.importers.csv_importer.open', mock_open(), create=True)
    mocker.patch('passpie.importers.csv_importer.csv.reader', return_value=iter([]))
    importer = CSVImporter()

    with pytest.raises(ValueError):
        importer.handle('filepath', cols=[])


def test_csv_importer_returns_list_of_credentials(mocker, mock_open):
    headers = ['Name', 'Login', 'Password', 'Comment']
    rows = [
        headers,
        ['example.com', 'foo', 'password', ''],
        ['example.com', 'bar', 'password', ''],
    ]
    expected_credentials = [
        {'name': 'example.com', 'login': 'foo', 'password': 'password', 'comment': ''},
        {'name': 'example.com', 'login': 'bar', 'password': 'password', 'comment': ''},
    ]
    cols = {h.lower(): idx for idx, h in enumerate(headers)}
    mocker.patch('passpie.importers.csv_importer.open', mock_open(), create=True)
    mocker.patch('passpie.importers.csv_importer.csv.reader', return_value=iter(rows))
    importer = CSVImporter()

    credentials = importer.handle('filepath', cols=cols)
    assert credentials == expected_credentials
