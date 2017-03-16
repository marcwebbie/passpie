# -*- coding: utf-8 -*-
import csv
import json
import os
import yaml

from passpie.cli import cli
from passpie.database import Database


def test_export_writes_to_stdout_when_path_is_dash(irunner, mocker):
    irunner.run("passpie add foo@bar spam@egg --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    db = Database('.passpie')
    decrypted_credentials = [dict(c) for c in db.all()]
    for cred in decrypted_credentials:
        cred['password'] = 'decrypted'

    result = irunner.passpie(
        "--passphrase passphrase export -"
    )

    assert result.exit_code == 0
    assert len(yaml.safe_load(result.output)) == len(decrypted_credentials)
    assert yaml.safe_load(result.output) == decrypted_credentials


def test_export_writes_json_to_stdout_when_path_is_dash_and_option_json_is_passed(irunner, mocker):
    irunner.run("passpie add foo@bar spam@egg --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    db = Database('.passpie')
    decrypted_credentials = [dict(c) for c in db.all()]
    for cred in decrypted_credentials:
        cred['password'] = 'decrypted'

    result = irunner.passpie(
        "--passphrase k export --json -"
    )

    assert result.exit_code == 0
    assert len(json.loads(result.output)) == len(decrypted_credentials)
    assert json.loads(result.output) == decrypted_credentials


def test_export_writes_csv_to_stdout_when_path_is_dash_and_option_csv_is_passed(irunner, mocker):
    irunner.run("passpie add foo@bar spam@egg --random")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    db = Database('.passpie')
    decrypted_credentials = [dict(c) for c in db.all()]
    for cred in decrypted_credentials:
        cred['password'] = 'decrypted'

    result = irunner.passpie(
        "--passphrase k export --csv credentials.csv"
    )

    assert result.exit_code == 0
    assert "credentials.csv" in os.listdir(".")
    with open('credentials.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            cred = {
                "name": row[0],
                "login": row[1],
                "password": row[2],
                "comment": row[3],
            }
            assert cred in decrypted_credentials


def test_export_writes_csv_handles_unicode(irunner, mocker):
    irunner.run(u"passpie add foo@bar spam@egg --random --comment l'éphémère")
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    result = irunner.passpie("--passphrase k export --csv -")

    assert result.exit_code == 0, result.output
    assert u"l'éphémère" in result.output
