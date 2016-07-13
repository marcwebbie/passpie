import yaml

from passpie.cli import cli
from passpie.database import CredentialFactory


def test_export_writes_to_stdout_when_path_is_dash(irunner, mocker):
    mocker.patch("passpie.database.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    irunner.db.insert(credential)
    result = irunner.run(cli, "--passphrase k export -")

    assert result.exit_code == 0, result.output
    assert yaml.safe_load(result.output) == {
        u'handler': 'passpie',
        u'version': 2.0,
        u"credentials": [credential],
    }
