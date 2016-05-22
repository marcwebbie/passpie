import os

from tinydb import where, Query
from tinydb.storages import MemoryStorage

from passpie.database import Database, PasspieStorage
from .helpers import MockerTestCase


class StorageTests(MockerTestCase):

    def setUp(self):
        self.mock_os = self.patch('passpie.database.os')
        self.mock_shutil = self.patch("passpie.database.shutil")
        self.storage = PasspieStorage("path")

    def test_read_returns_all_found_credentials_in_default_dict(self):
        mock_open = self.patch("passpie.database.open",
                               self.mock_open(), create=True)
        mock_open().read.return_value = "{}"
        self.mock_os = self.patch('passpie.database.os')
        self.mock_os.walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('eggs.pass',)),
            ('/foo/bar2', (), ('spam.pass',))
        ]
        storage = PasspieStorage("path")
        storage.write = self.Mock()
        elements = storage.read()
        self.assertIn("_default", elements.keys())
        self.assertEqual(len(elements["_default"]), 2)

    def test_write_writes_all_elements_from_data_default_dict(self):
        mock_mkdir_open = self.patch("passpie.database.mkdir_open",
                                     self.mock_open(), create=True)

        self.patch("passpie.database.PasspieStorage.read",
                   return_value={"_default": {}})
        data = {"_default": {1: {"name": "example", "login": "foo"},
                             2: {"name": "example", "login": "bar"}}}
        storage = PasspieStorage("path")

        storage.write(data)

        self.assertEqual(mock_mkdir_open.call_count, 2)

    def test_delete_removes_credentials_files(self):
        credentials = [
            {"name": "bar", "login": "foo"},
            {"name": "spam", "login": "foozy"},
        ]

        self.storage.delete(credentials)

        for cred in credentials:
            credpath = self.mock_os.path.join(cred["name"], cred["login"])
            self.mock_os.remove.assert_any_call(credpath)

    def test_delete_removes_empty_directories(self):
        credentials = [
            {"name": "bar", "login": "foo"},
            {"name": "spam", "login": "foozy"},
        ]
        self.mock_os.listdir.side_effect = [[], ["not empty"]]
        self.storage.delete(credentials)

        credpath = self.mock_os.path.join(credentials[0]["name"],
                                          credentials[0]["login"])
        self.mock_shutil.rmtree.assert_called_once_with(
            self.mock_os.path.dirname(credpath))


def test_database_has_keys_returns_true_when_file_dot_keys_found_in_db_path(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    mock_exists = mocker.patch('passpie.database.os.path.exists', return_value=True)
    mock_join = mocker.patch('passpie.database.os.path.join')
    db = Database(config)

    assert db.has_keys() is True
    mock_exists.assert_called_once_with(mock_join('path', '.keys'))


def test_database_credential_with_fullname_does_a_db_where_with_split_fullname(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch('passpie.database.split_fullname', return_value=('login', 'name'))
    mock_get = mocker.patch.object(db, 'get', return_value=[{}])

    result = db.credential('login@name')
    assert db.get.called
    assert result == [{}]
    db.get.assert_called_once_with((where('login') == 'login') & (where('name') == 'name'))


def test_database_credential_with_fullname_does_a_db_get_with_filtering_name_only(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch('passpie.database.split_fullname', return_value=(None, 'example.com'))
    mock_get = mocker.patch.object(db, 'get', return_value=[{}])
    Credential = Query()

    result = db.credential('login@name')

    assert db.get.called
    db.get.assert_called_once_with(Credential.name == "example.com")


def test_database_credential_with_fullname_does_a_db_where_with_split_fullname(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch('passpie.database.split_fullname', return_value=('login', 'name'))
    mock_get = mocker.patch.object(db, 'get', return_value=[{}])

    result = db.credential('login@name')
    assert db.get.called
    assert result == [{}]
    db.get.assert_called_once_with((where('login') == 'login') & (where('name') == 'name'))


def test_database_add_insert_credential_to_database(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mock_get = mocker.patch.object(db, 'insert')
    mocker.patch('passpie.database.split_fullname', return_value=('login', 'name'))
    mock_datetime = mocker.patch('passpie.database.datetime')
    credential = dict(fullname='login@name',
                      name='name',
                      login='login',
                      password='password',
                      comment='comment',
                      modified=mock_datetime.now())

    db.add(fullname='login@name', password='password', comment='comment')
    assert db.insert.called
    db.insert.assert_called_once_with(credential)


def test_database_add_with_empty_login_logs_error_and_return_none(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch('passpie.database.split_fullname', return_value=(None, 'name'))
    mock_logging = mocker.patch('passpie.database.logging')

    result = db.add(fullname='login@name', password='password', comment='comment')
    assert result is None
    mock_logging.error.assert_called_once_with(
        'Cannot add credential with empty login. use "@<name>" syntax')


def test_database_update_uses_table_update_credential_to_database(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'table', mocker.MagicMock())
    mocker.patch('passpie.database.make_fullname', return_value='login@name')
    mock_datetime = mocker.patch('passpie.database.datetime')
    values = {
        'login': 'login',
        'name': 'name',
        'comment': 'new comment'
    }

    db.update(fullname='login@name', values=values)
    query = (Query().login == 'login') & (Query().name == 'name')

    assert db.table().update.called
    db.table().update.assert_called_once_with(values, query)


def test_database_remove_uses_table_remove_credential_from_database(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'table', mocker.MagicMock())
    mocker.patch('passpie.database.make_fullname', return_value='login@name')

    db.remove(fullname='login@name')

    assert db.table().remove.called
    db.table().remove.assert_called_once_with((where('fullname') == 'login@name'))


def test_credentials_returns_sorted_list_credentials(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'all', mocker.MagicMock())
    mock_sorted = mocker.patch('passpie.database.sorted', create=True)

    credentials = db.credentials()
    assert credentials == mock_sorted()


def test_credentials_filter_credentials_by_login_and_name_when_full_fullname_passed(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch('passpie.database.split_fullname', return_value=('foo', 'example.com'))
    mocker.patch.object(db, 'search')
    mocker.patch.object(db, 'all')
    Credential = Query()

    credentials = db.credentials(fullname="foo@example.com")
    assert db.search.called is True
    assert db.all.called is False
    db.search.assert_called_once_with(
        (Credential.login == 'foo') & (Credential.name == 'example.com')
    )


def test_credentials_filter_credentials_by_login_and_name_when_empty_login_fullname_passed(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'search')
    mocker.patch.object(db, 'all')
    mocker.patch('passpie.database.split_fullname', return_value=('', 'example.com'))
    Credential = Query()

    credentials = db.credentials(fullname="@example.com")
    assert db.search.called is True
    assert db.all.called is False
    db.search.assert_called_once_with(
        (Credential.login == "") & (Credential.name == "example.com")
    )


def test_credentials_filter_credentials_by_login_and_name_when_name_only_fullname_passed(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'search')
    mocker.patch.object(db, 'all')
    mocker.patch('passpie.database.split_fullname', return_value=(None, 'example.com'))
    Credential = Query()

    credentials = db.credentials(fullname="@example.com")
    assert db.search.called is True
    assert db.all.called is False
    db.search.assert_called_once_with(
        (Credential.name == "example.com")
    )


def test_database_matches_uses_table_remove_credential_from_database(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    mocker.patch.object(db, 'search', mocker.MagicMock())
    mocker.patch('passpie.database.make_fullname', return_value='login@name')
    regex = '.*'
    Credential = Query()
    result = db.matches(regex=regex)

    assert db.search.called
    assert isinstance(result, list)
    db.search.assert_called_once_with(
        Credential.name.matches(regex) |
        Credential.login.matches(regex) |
        Credential.comment.matches(regex)
    )

def test_database_filename_returns_expected_filename_of_credential(mocker):
    config = {
        'path': 'path',
        'extension': '.pass',
    }
    db = Database(config)
    assert db.filename("login@name") == os.path.normpath("path/name/login.pass")
    assert db.filename("@name") == os.path.normpath("path/name/.pass")
