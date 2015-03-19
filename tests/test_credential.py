from .helpers import MockerTestCase
from passpie.credential import split_fullname, make_fullname


class CredentialTests(MockerTestCase):

    def test_split_fullname_raises_value_error_when_invalid_name(self):
        invalid_fullname = ""
        with self.assertRaises(ValueError):
            split_fullname(invalid_fullname)

    def test_split_fullname_returns_expected_login_and_name(self):
        self.assertEqual(split_fullname("foo@bar"), ("foo", "bar"))
        self.assertEqual(split_fullname("foo@bar.com"), ("foo", "bar.com"))
        self.assertEqual(split_fullname("@bar"), ("_", "bar"))
        self.assertEqual(
            split_fullname("foo@example.com@bar"), ("foo@example.com", "bar"))

    def test_make_fullname_returns_expected_fullname(self):
        self.assertEqual(make_fullname("foo", "bar"), "foo@bar")
        self.assertEqual(make_fullname("_", "bar"), "_@bar")
        self.assertEqual(make_fullname(None, "bar"), "_@bar")
