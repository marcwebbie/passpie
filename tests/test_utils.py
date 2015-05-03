try:
    from mock import mock_open
except:
    from unittest.mock import mock_open

import yaml

from passpie.utils import genpass, mkdir_open, load_config, get_version
from .helpers import MockerTestCase


class UtilsTests(MockerTestCase):

    def test_genpass_generates_a_password_with_length_32(self):
        password = genpass()
        self.assertEqual(len(password), 32)

    def test_mkdir_open_makedirs_on_path_dirname(self):
        mock_os = self.patch("passpie.utils.os")
        self.patch("passpie.utils.open", self.mock_open(), create=True)
        path = "path/to/foo.pass"
        with mkdir_open(path, "w"):
            dirname = mock_os.path.dirname(path)
            mock_os.makedirs.assert_called_once_with(dirname)

    def test_mkdir_open_handle_oserror_for_file_exist(self):
        mock_os = self.patch("passpie.utils.os")
        self.patch("passpie.utils.open", self.mock_open(), create=True)
        path = "path/to/foo.pass"

        mock_os.makedirs.side_effect = OSError(17, "File Exists")
        with mkdir_open(path, "w") as fd:
            self.assertIsNotNone(fd)

        mock_os.makedirs.side_effect = OSError(2, "File Not Found")
        with self.assertRaises(OSError):
            with mkdir_open(path, "w") as fd:
                pass


def test_load_config_replaces_sets_user_config_element(mocker):
    DEFAULT_CONFIG = {'path': 'default_path', 'short_commands': True}
    USER_CONFIG = {'path': 'user_path'}
    mocker.patch('passpie.utils.os.path.exists', return_value=True)
    mocker.patch('passpie.utils.os.path.isfile', return_value=True)
    mocker.patch('passpie.utils.open', mock_open(), create=True)
    mocker.patch('passpie.utils.yaml.load', return_value=USER_CONFIG)

    config = load_config(DEFAULT_CONFIG, 'configrc')

    assert config.path == USER_CONFIG['path']
    assert config.short_commands == DEFAULT_CONFIG['short_commands']


def test_load_config_logs_debug_message_when_malformed_config(mocker):
    mocker.patch('passpie.utils.open', mock_open(), create=True)
    mocker.patch('passpie.utils.os.path.exists', return_value=True)
    mocker.patch('passpie.utils.os.path.isfile', return_value=True)
    mocker.patch('passpie.utils.yaml.load',
                 side_effect=yaml.scanner.ScannerError)
    mock_logging = mocker.patch('passpie.utils.logging')

    load_config({}, {})

    assert mock_logging.debug.called


def test_get_version_uses_get_distribution_to_find_version(mocker):
    expected_version = '1.0'
    mock_dist = mocker.patch('passpie.utils.get_distribution')()
    mock_dist.location = 'applications'
    mock_dist.version = expected_version
    mocker.patch('passpie.utils.os.path.normcase')
    mocker.patch('passpie.utils.os.path.join')

    version = get_version()

    assert version == '1.0'


def test_get_version_returns_install_message_when_dist_not_found(mocker):
    message = 'Please install this project with setup.py or pip'
    mocker.patch('passpie.utils.get_distribution')
    mocker.patch('passpie.utils.os.path.normcase',
                 side_effect=['path1', 'path2'])

    version = get_version()

    assert version == message
