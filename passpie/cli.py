from argparse import Namespace
from datetime import datetime, timedelta
from pkg_resources import get_distribution, DistributionNotFound
import functools
import json
import os
import shutil
import tempfile

from tabulate import tabulate
from tinydb.queries import where
import click
import pyperclip
import yaml

from ._compat import FileExistsError
from .credential import split_fullname, make_fullname
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
    __version__ = 'Please install this project with setup.py or pip'
else:
    __version__ = _dist.version


CONFIG_PATH = os.path.expanduser('~/.passpierc')

config_dict = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        config_content = f.read()

    try:
        config_dict = yaml.load(config_content)
        for k in ('path', 'show_password', 'headers', 'colors', 'table_format'):
            assert k in config_dict
    except (AssertionError, yaml.scanner.ScannerError) as e:
        click.ClickException('Bad configuration file: {}'.format(e))

config = Namespace(
    path=config_dict.get('path', os.path.expanduser("~/.passpie")),
    show_password=config_dict.get('show_password', False),
    short_commands=config_dict.get('short_commands', False),
    table_format=config_dict.get('table_format', "fancy_grid"),
    headers=config_dict.get(
        'headers',
        ["name", "login", "password", "comment"]),
    colors=config_dict.get(
        'colors',
        {"name": "yellow", "login": "green", "password": "magenta"}),
)


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


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
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))
    return credential


def ensure_passphrase(db, passphrase):
    try:
        with Cryptor(db._storage.path) as cryptor:
            cryptor.check(passphrase, ensure=True)
        return passphrase
    except ValueError:
        message = 'Wrong passphrase'
        raise click.ClickException(click.style(message, fg='red'))


def print_table(credentials):
    if credentials:
        for credential in credentials:
            credential['password'] = "*****"
            headers = config.headers

        for header, color in config.colors.items():
            for credential in credentials:
                credential[header] = click.style(credential[header], fg=color)

        for credential in [c for c in credentials if 'name' in c.keys()]:
            credential['name'] = click.style(credential['name'], bold=True)

        for credential in [c for c in credentials if 'login' in c.keys()]:
            credential['login'] = click.style(credential['login'], bold=True)

        click.echo(Table(credentials).render(headers))


def ensure_database(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        keys_path = os.path.join(config.path, '.keys')
        if os.path.isdir(config.path) and os.path.isfile(keys_path):
            return func(*args, **kwargs)
        else:
            message = 'Not initialized database at {.path}'.format(config)
            raise click.ClickException(click.style(message, fg='yellow'))
    return decorator


@click.group(cls=AliasedGroup if config.short_commands else click.Group,
             invoke_without_command=True)
@click.option('-D', '--database', help='Alternative database path',
              type=click.Path(dir_okay=True, writable=True, resolve_path=True))
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database=config.path):
    if database:
        config.path = database
    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        credentials = sorted(db.all(), key=lambda x: x["name"]+x["login"])
        print_table(credentials)


@cli.command(name='config', help='Show configuration')
def print_config():
    print(yaml.dump(vars(config), default_flow_style=False))


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
        message = "Database exists in {}. `--force` to overwrite".format(
            config.path)
        raise click.ClickException(click.style(message, fg='yellow'))
    click.echo("Initialized database in {}".format(config.path))


@cli.command(help="Add new credential")
@click.argument("fullname")
@click.option('-r', '--random', 'password', flag_value=genpass())
@click.password_option(help="Credential password")
@click.option('-c', '--comment', default="", help="Credential comment")
@ensure_database
def add(fullname, password, comment):
    db = Database(config.path)
    try:
        login, name = split_fullname(fullname)
    except ValueError:
        message = 'invalid fullname syntax'
        raise click.ClickException(click.style(message, fg='yellow'))

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
        message = "Credential {} already exists. --force to overwrite".format(
            fullname)
        raise click.ClickException(click.style(message, fg='yellow'))


@cli.command(help="Update credential")
@click.argument("fullname")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.option("--comment", help="Credential new comment")
@click.option("--password", help="Credential new password")
@click.option('--random', 'password', flag_value=genpass(),
              help="Credential new randomly generated password")
def update(fullname, name, login, password, comment):
    db = Database(config.path)
    credential = get_credential_or_abort(db, fullname)
    values = credential.copy()

    if any([name, login, password, comment]):
        values["name"] = name if name else credential["name"]
        values["login"] = login if login else credential["login"]
        values["password"] = password if password else credential["password"]
        values["comment"] = comment if comment else credential["comment"]
    else:
        values["name"] = click.prompt("Name", default=credential["name"])
        values["login"] = click.prompt("Login", default=credential["login"])
        values["password"] = click.prompt("Password",
                                          hide_input=True,
                                          default=credential["password"],
                                          confirmation_prompt=True,
                                          show_default=False,
                                          prompt_suffix=" [*****]: ")
        values["comment"] = click.prompt("Comment",
                                         default=credential["comment"])

    if values != credential:
        values["fullname"] = make_fullname(values["login"], values["name"])
        values["modified"] = datetime.now()
        if values["password"] != credential["password"]:
            with Cryptor(config.path) as cryptor:
                values["password"] = cryptor.encrypt(password)
        db = Database(config.path)
        db.update(values, (where("fullname") == credential["fullname"]))


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


@cli.command(help='Renew passpie password and re-encrypt credentials')
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
def reset(passphrase):
    db = Database(config.path)
    ensure_passphrase(db, passphrase)
    credentials = db.all()

    # decrypt passwords
    with Cryptor(config.path) as cryptor:
        for cred in credentials:
            cred["password"] = cryptor.decrypt(cred["password"], passphrase)

    new_passphrase = click.prompt('New passphrase',
                                  hide_input=True, confirmation_prompt=True)

    # remove old credentials
    tempdir = tempfile.mkdtemp()
    with Cryptor(tempdir) as cryptor:
        cryptor.create_keys(new_passphrase)
        for cred in credentials:
            cred["password"] = cryptor.encrypt(cred["password"])

    # replace old database with tempdir
    shutil.rmtree(config.path)
    os.rename(tempdir, config.path)
