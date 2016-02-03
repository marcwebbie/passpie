import pytest

from passpie.importers.keepass_importer import KeepassImporter


def test_keepass_importer_returns_false_when_csv_files_hasnt_expected_headers(mocker, mock_open):
    headers = reversed(['Group', 'Title', 'Username', 'Password', 'URL', 'Notes'])
    mocker.patch('passpie.importers.keepass_importer.unicode_csv_reader',
                 return_value=iter([headers]))
    mocker.patch('passpie.importers.keepass_importer.open', mock_open(), create=True)

    result = KeepassImporter().match('filepath')
    assert result is False


def test_keepass_importer_with_empty_reader_raises_value_error(mocker, mock_open):
    mocker.patch('passpie.importers.keepass_importer.open', mock_open(), create=True)
    mocker.patch('passpie.importers.keepass_importer.unicode_csv_reader',
                 return_value=iter([]))
    importer = KeepassImporter()

    with pytest.raises(ValueError):
        importer.match('filepath')

    with pytest.raises(ValueError):
        importer.handle('filepath')


def test_keepass_importer_returns_true_when_csv_files_has_expected_headers(mocker, mock_open):
    headers = ['Group', 'Title', 'Username', 'Password', 'URL', 'Notes']
    mocker.patch('passpie.importers.keepass_importer.unicode_csv_reader',
                 return_value=iter([headers]))
    mocker.patch('passpie.importers.keepass_importer.open', mock_open(), create=True)

    result = KeepassImporter().match('filepath')
    assert result is True


def test_keepass_importer_returns_expected_credentials_for_row(mocker, mock_open):
    rows = [
        ['Group', 'Title', 'Username', 'Password', 'URL', 'Notes'],
        ['Root', 'Email', 'foo', 'password', 'example.org', ''],
        ['Root', 'Email', 'foo', 'password', 'example.com', 'Some comment'],
    ]
    credential1 = {
        'login': 'foo',
        'name': 'example.org',
        'comment': '',
        'password': 'password'
    }
    credential2 = {
        'login': 'foo',
        'name': 'example.com',
        'comment': 'Some comment',
        'password': 'password'
    }
    mocker.patch('passpie.importers.keepass_importer.unicode_csv_reader',
                 return_value=iter(rows))
    mocker.patch('passpie.importers.keepass_importer.open', mock_open(), create=True)

    result = KeepassImporter().handle('filepath')
    credentials = result
    assert credentials
    assert credential1 in credentials
    assert credential2 in credentials
