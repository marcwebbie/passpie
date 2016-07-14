import json
import yaml

from passpie.cli import cli
from passpie.database import CredentialFactory


def test_export_writes_to_stdout_when_path_is_dash(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    irunner.db.insert(credential)
    result = irunner.passpie("--passphrase k export -")
    expected_output = [dict(irunner.db.decrypt(credential))]

    assert result.exit_code == 0, result.output
    assert yaml.safe_load(result.output) == yaml.safe_load(yaml.safe_dump(expected_output))


def test_export_writes_json_to_stdout_when_path_is_dash_and_option_json_is_passed(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    irunner.db.insert(credential)
    result = irunner.passpie("--passphrase k export --json -")
    expected_output = [dict(irunner.db.decrypt(credential))]

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == json.loads(json.dumps(expected_output))
