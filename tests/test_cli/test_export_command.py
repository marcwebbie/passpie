import yaml

from passpie.cli import cli
from passpie.database import CredentialFactory


def test_export_writes_to_stdout_when_path_is_dash(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    irunner.db.insert(credential)
    result = irunner.run(cli, "--passphrase k export -")
    expected_output_dict = {
        'handler': 'passpie',
        'version': 2.0,
        "credentials": [dict(irunner.db.decrypt(credential))],
    }

    assert result.exit_code == 0, result.output
    assert yaml.safe_load(result.output) == yaml.safe_load(yaml.safe_dump(expected_output_dict))
