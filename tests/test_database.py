from passpie.database import PasspieStorage
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
