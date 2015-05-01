from argparse import Namespace
from datetime import datetime, timedelta
from pkg_resources import get_distribution, DistributionNotFound
import json
import os
import shutil

from tabulate import tabulate
from tinydb.queries import where
import click
import pyperclip
import yaml

from ._compat import FileExistsError
from .credential import split_fullname
from .crypt import Cryptor
from .database import Database
from .utils import genpass


try:
    _dist = get_distribution('passpie')
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'passpie')):
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version

config = Namespace(
    path=os.path.expanduser("~/.passpie"),
    show_password=False,
    headers=("name", "login", "password", "comment"),
    colors={"name": "yellow", "login": "green", "password": "magenta"},
    table_format="fancy_grid"
)


class Table(object):
    """Reprensent table outputs"""

    def __init__(self, data):
        self.data = data
        self.tablefmt = config.table_format

    def __getitem__(self, keys):
        if isinstance(keys, str):
            keys = (keys,)
        return [[e[k] for k in keys]
                for e in self.data]

    def render(self, keys):
        return tabulate(self[keys],
                        headers=[k.title() for k in keys],
                        tablefmt=self.tablefmt)


def get_credential_or_abort(db, fullname):
    credential = db.get(where("fullname") == fullname)
    if not credential:
        click.secho(
            "Credential '{}' not found".format(fullname), fg="red")
        raise click.Abort
    return credential


def ensure_passphrase(db, passphrase):
    try:
        with Cryptor(db._storage.path) as cryptor:
            cryptor.check(passphrase, ensure=True)
        return passphrase
    except ValueError:
        click.secho("Wrong passphrase", fg="red")
        raise click.Abort


def print_table(credentials):
    if credentials:
        for credential in credentials:
            credential['password'] = "*****"
            headers = config.headers

        for header, color in config.colors.items():
            for credential in credentials:
                credential[header] = click.style(credential[header], fg=color)

        click.echo(Table(credentials).render(headers))


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        credentials = sorted(db.all(), key=lambda x: x["name"]+x["login"])
        print_table(credentials)


@cli.command(help="Initialize new passpie database")
@click.option('--passphrase', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--force', is_flag=True, help="force overwrite database")
def init(passphrase, force):
    if force:
        shutil.rmtree(config.path)

    try:
        with Cryptor(config.path) as cryptor:
            cryptor.create_keys(passphrase)
    except FileExistsError:
        msg = "Database exists in {}. `--force` to overwrite"
        click.secho(msg.format(config.path), fg="yellow")
        raise click.Abort
    click.echo("Initialized database in {}".format(config.path))


@cli.command(help="Add new credential")
@click.argument("fullname")
@click.option('-r', '--random', 'password', flag_value=genpass())
@click.password_option(help="Credential password")
@click.option('-c', '--comment', default="", help="Credential comment")
def add(fullname, password, comment):
    db = Database(config.path)
    try:
        login, name = split_fullname(fullname)
    except ValueError:
        click.secho('invalid fullname syntax', fg='yellow')
        raise click.Abort

    found = db.get((where("login") == login) & (where("name") == name))
    if not found:
        with Cryptor(config.path) as cryptor:
            encrypted = cryptor.encrypt(password)

        credential = dict(fullname=fullname,
                          name=name,
                          login=login,
                          password=encrypted,
                          comment=comment,
                          modified=datetime.now())
        db.insert(credential)
    else:
        click.echo("Credential {} already exists.".format(fullname))
        raise click.Abort


@cli.command(help="Remove credential")
@click.argument("fullname")
def remove(fullname):
    db = Database(config.path)
    credential = get_credential_or_abort(db, fullname)
    if credential:
        click.confirm(
            'Remove credential: {}'.format(click.style(fullname, 'yellow')),
            abort=True
        )
        db.remove(where('fullname') == credential["fullname"])


@cli.command(help="Copy credential password to clipboard")
@click.argument("fullname")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
def copy(fullname, passphrase):
    db = Database(config.path)
    credential = get_credential_or_abort(db, fullname)
    ensure_passphrase(db, passphrase)
    with Cryptor(config.path) as cryptor:
        decrypted = cryptor.decrypt(credential["password"],
                                    passphrase=passphrase)
        pyperclip.copy(decrypted)
        click.secho("Password copied to clipboard".format(
            credential["fullname"]), fg="yellow")


@cli.command(help="Search credentials by regular expressions")
@click.argument("regex")
def search(regex):
    db = Database(config.path)
    credentials = db.search(
        where("name").matches(regex) |
        where("login").matches(regex) |
        where("comment").matches(regex))
    credentials = sorted(credentials, key=lambda x: x["name"]+x["login"])
    print_table(credentials)


@cli.command(help="Diagnose database for improvements")
@click.option("--full", is_flag=True, help="Show all entries")
@click.option("--days", default=90, type=int, help="Elapsed days")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
def status(full, days, passphrase):
    db = Database(config.path)
    ensure_passphrase(db, passphrase)
    credentials = sorted(db.all(), key=lambda x: x["name"]+x["login"])
    with Cryptor(config.path) as cryptor:
        for cred in credentials:
            cred["password"] = cryptor.decrypt(cred["password"], passphrase)

    if credentials:
        # check passwords
        for cred in credentials:
            repeated = [
                c["fullname"] for c in credentials
                if c["password"] == cred["password"] and c != cred
            ]
            if repeated:
                password = "Same as: {}".format(repeated)
                cred["repeated"] = click.style(password, "red")
            else:
                cred["repeated"] = click.style("OK", "green")

        for cred in credentials:
            cred['password'] = cred['repeated']

        # check modified time
        for cred in credentials:
            modified_delta = (datetime.now() - cred["modified"])
            if modified_delta > timedelta(days=days):
                modified_time = "{} days ago".format(modified_delta.days)
                cred["modified"] = click.style(modified_time, "red")

            else:
                cred["modified"] = click.style("OK", "green")

        if not full:
            credentials = [c for c in credentials
                           if c["password"] or c["modified"]]

        table = Table(credentials)
        click.echo(table.render(["name", "login", "password", "modified"]))


@cli.command(name="export", help="Export credentials in plain text")
@click.argument("dbfile", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
def export_database(dbfile, as_json, passphrase):
    db = Database(config.path)
    ensure_passphrase(db, passphrase)
    credentials = sorted(db.all(), key=lambda x: x["name"]+x["login"])
    with Cryptor(config.path) as cryptor:
        for cred in credentials:
            cred["password"] = cryptor.decrypt(cred["password"], passphrase)

    if as_json:
        for cred in credentials:
            cred["modified"] = str(cred["modified"])
        dict_content = {
            'handler': 'passpie',
            'version': 1.0,
            'credentials': [dict(x) for x in credentials],
        }
        content = json.dumps(dict_content, indent=2)
    else:
        dict_content = {
            'handler': 'passpie',
            'version': 1.0,
            'credentials': [dict(x) for x in credentials],
        }
        content = yaml.dump(dict_content, default_flow_style=False)

    dbfile.write(content)


@cli.command(name="import", help="Import credentials from path")
@click.argument("path", type=click.Path())
def import_database(path):
    from passpie.importers import find_importer
    importer = find_importer(path)
    credentials = importer.handle(path)
    db = Database(config.path)
    with Cryptor(config.path) as cryptor:
        for cred in credentials:
            encrypted = cryptor.encrypt(cred['password'])
            cred['password'] = encrypted
        db.insert_multiple(credentials)
