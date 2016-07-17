# -*- coding: utf-8 -*-
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


def test_export_writes_csv_to_stdout_when_path_is_dash_and_option_csv_is_passed(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    irunner.db.insert(credential)
    result = irunner.passpie("--passphrase k export --csv -")
    decrypted_credential = dict(irunner.db.decrypt(credential))
    row_header = ["name", "login", "password", "comment"]
    row_credential = [
        decrypted_credential["name"],
        decrypted_credential["login"],
        decrypted_credential["password"],
        decrypted_credential["comment"],
    ]
    expected_output = "{}\n{}\n".format(
        ",".join(row_header),
        ",".join(row_credential))

    assert result.exit_code == 0, result.output
    assert result.output == expected_output


def test_export_writes_csv_handles_unicode(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(comment=u"l'éphémère")
    irunner.db.insert(credential)
    result = irunner.passpie("--passphrase k export --csv -")
    decrypted_credential = dict(irunner.db.decrypt(credential))

    assert result.exit_code == 0, result.output
    assert u"l'éphémère" in result.output
