# -*- coding: utf-8 -*-
import json
import yaml

from passpie.cli import cli
from passpie.database import CredentialFactory


EXPORTED_PLAIN_TEXT_YAML = """
- comment: Ipsum deleniti praesentium voluptatum.
  login: bennettjodi
  name: hurst.com
  password: '@_iKo#+Yu8'
- comment: Sit unde numquam voluptas.
  login: melissaperez
  name: ford.com
  password: '&qDn_PFWG7Z7b0RrlfCE1Xr0@N1#oPMQ'
"""

EXPORTED_PLAIN_TEXT_KEEPASS_CSV = u'''"Group","Title","Username","Password","URL","Notes"
"Root","Some Title","john.doe","secret","example.com","Some comments"
"Root","Another title","foo.bar","p4ssword","example.org",""
"Root","Crazy title","oof","password","example.org",""
"Root","Hard password credential","egg","+[-g9jTY%x.m-*3x,(;}]U5;aAU*BU2g","example.org",""
"Root","Unicode credential","josé","™£¢∞§¶•ªºœ∑´®†¥¨ˆøß∂ƒ©˙∆˚¬Ω≈ç√∫~µ≤","example.org","Main mail"
'''


def test_import_default_passpie_yaml_exported(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    with open("credentials.txt", "w") as f:
        f.write(EXPORTED_PLAIN_TEXT_YAML)
    result = irunner.passpie("import credentials.txt")

    assert result.exit_code == 0, result.output
    assert len(irunner.db.all()) == 2


def test_import_csv_keepass_credential(irunner, mocker):
    mocker.patch("passpie.cli.GPG.decrypt", return_value="decrypted")
    credential = CredentialFactory(fullname="foo@bar")
    with open("keepass.csv", "w") as f:
        f.write(EXPORTED_PLAIN_TEXT_KEEPASS_CSV.encode("utf-8"))
    result = irunner.passpie('import --skip-lines 1 --csv ",,login,password,name,comment" keepass.csv')

    assert result.exit_code == 0, result.output
    assert len(irunner.db.all()) == 5, result.output
