from .helpers import MockerTestCase
from passpie.utils import genpass, mkdir_open


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
