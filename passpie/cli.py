from datetime import datetime, timedelta
from functools import partial
import json
import logging
import os
import shutil
import re

from tinydb.queries import where
import click
import yaml

from . import completion, clipboard
from ._compat import *
from .credential import split_fullname, make_fullname
from .crypt import Cryptor
from .database import Database
from .importers import find_importer
from .utils import genpass, load_config, ensure_dependencies, logger
from .table import Table
from .history import Repository


__version__ = "0.3.3"

USER_CONFIG_PATH = os.path.expanduser('~/.passpierc')
DEFAULT_CONFIG = {
    'path': os.path.expanduser('~/.passpie'),
    'short_commands': False,
    'genpass_length': 32,
    'genpass_symbols': "_-#|+=",
    'table_format': 'fancy_grid',
    'headers': ['name', 'login', 'password', 'comment'],
    'colors': {'name': 'yellow', 'login': 'green'},
    'repo': True,
    'search_automatic_regex': False,
    'status_repeated_passwords_limit': 5
}
config = load_config(DEFAULT_CONFIG, USER_CONFIG_PATH)
genpass = partial(genpass,
                  length=config.genpass_length,
                  special=config.genpass_symbols)


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
        message = 'Too many matches: %s' % ', '.join(
            sorted([click.style(m, fg='yellow') for m in matches])
        )
        ctx.fail(message)


def get_credential_or_abort(db, fullname, many=False):
    try:
        login, name = split_fullname(fullname)
        query = (where("name") == name) & (where("login") == login)
    except ValueError:
        query = where('name') == fullname

    found = db.search(query) if many else db.get(query)
    if not found:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))
    elif db.count(query) > 1 and not many:
        message = "Multiple matches for '{}'".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    return found


def ensure_is_database(path):
    try:
        assert os.path.isdir(path)
        assert os.path.isfile(os.path.join(path, '.keys'))
    except AssertionError:
        message = 'Not initialized database at {.path}'.format(config)
        raise click.ClickException(click.style(message, fg='yellow'))


def ensure_passphrase(db, passphrase):
    try:
        with Cryptor(db._storage.path) as cryptor:
            cryptor.check(passphrase, ensure=True)
        return passphrase
    except ValueError:
        message = 'Wrong passphrase'
        raise click.ClickException(click.style(message, fg='red'))


def print_table(credentials):
    from .table import Table

    if credentials:
        table = Table(
            config.headers,
            table_format=config.table_format,
            colors=config.colors,
            hidden=['password']
        )
        click.echo(table.render(credentials))


@click.group(cls=AliasedGroup if config.short_commands else click.Group,
             invoke_without_command=True)
@click.option('-D', '--database', help='Alternative database path',
              type=click.Path(dir_okay=True, writable=True, resolve_path=True))
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, verbose):
    try:
        ensure_dependencies()
    except RuntimeError as e:
        raise click.ClickException(click.style(str(e), fg='red'))

    if database:
        config.path = database

    if verbose:
        logger.setLevel(logging.DEBUG)

    if not ctx.invoked_subcommand == 'init':
        ensure_is_database(config.path)

    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        credentials = sorted(db.all(), key=lambda x: x["name"] + x["login"])
        print_table(credentials)


@cli.command(help='Shows completion scripts')
@click.argument('shell_name', type=click.Choice(completion.SHELLS),
                default=None, required=False)
@click.option('--commands', default=None)
def complete(shell_name, commands):
    commands = ['add', 'copy', 'remove', 'search', 'update']
    script = completion.script(shell_name, config.path, commands)
    click.echo(script)


@cli.command(help="Initialize new passpie database")
@click.option('--passphrase', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--force', is_flag=True, help="Force overwrite database")
@click.option('--no-repo', is_flag=True, help="Don't create a repo repository")
def init(passphrase, force, no_repo):
    if force and os.path.isdir(config.path):
        shutil.rmtree(config.path)

    try:
        with Cryptor(config.path) as cryptor:
            cryptor.create_keys(passphrase)
        if config.repo and not no_repo:
            repo = Repository(config.path)
            repo.init()
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
@click.option('-f', '--force', is_flag=True, help="Force overwriting")
@click.option('-C', '--copy', is_flag=True, help="Copy password to clipboard")
def add(fullname, password, comment, force, copy):
    db = Database(config.path)
    try:
        login, name = split_fullname(fullname)
    except ValueError:
        message = 'invalid fullname syntax'
        raise click.ClickException(click.style(message, fg='yellow'))

    found = db.get((where("login") == login) & (where("name") == name))
    if force or not found:
        with Cryptor(config.path) as cryptor:
            encrypted = cryptor.encrypt(password)

        credential = dict(fullname=fullname,
                          name=name,
                          login=login,
                          password=encrypted,
                          comment=comment,
                          modified=datetime.now())
        db.insert(credential)
        if copy:
            clipboard.copy(password)

        repo = Repository(config.path)
        message = 'Added {}'.format(credential['fullname'])
        repo.commit(message=message)
        logger.debug(message)
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
                values["password"] = cryptor.encrypt(values['password'])
        db = Database(config.path)
        db.update(values, (where("fullname") == credential["fullname"]))

        message = 'Updated {}'.format(credential['fullname'])
        logger.debug(message)
        repo = Repository(config.path)
        repo.commit(message)


@cli.command(help="Remove credential")
@click.argument("fullname")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def remove(fullname, yes):
    db = Database(config.path)
    credentials = get_credential_or_abort(db, fullname, many=True)

    if credentials:
        if not yes:
            creds = ', '.join([c['fullname'] for c in credentials])
            click.confirm(
                'Remove credentials: ({})'.format(
                    click.style(creds, 'yellow')),
                abort=True
            )
        for credential in credentials:
            db.remove(where('fullname') == credential['fullname'])

        fullnames = ', '.join(c['fullname'] for c in credentials)
        message = 'Removed {}'.format(fullnames)
        logger.debug(message)
        repo = Repository(config.path)
        repo.commit(message)


@cli.command(help="Copy credential password to clipboard/stdout")
@click.argument("fullname")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@click.option("--to", default='clipboard',
              type=click.Choice(['stdout', 'clipboard']))
@click.option("--clear", default=0)
@pass_db
def copy(db, fullname, passphrase, to, clear):
    clear = clear if clear else config['copy_timeout']
    credential = db.credential(fullname)
    if not credential:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    with GPG(db.path) as gpg:
        decrypted = gpg.decrypt(credential["password"], passphrase=passphrase)
        if to == 'clipboard':
            clipboard.copy(decrypted, clear)
        elif to == 'stdout':
            click.echo(decrypted)


@cli.command(help="Search credentials by regular expressions")
@click.argument("regex")
@pass_db
def search(db, regex):
    credentials = db.matches(regex)
    if credentials:
        table = Table(
            config['headers'],
            table_format=config['table_format'],
            colors=config['colors'],
            hidden=['password']
        )
        click.echo(table.render(credentials))


@cli.command(help='Renew passpie database and re-encrypt credentials')
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@pass_db
def reset(db, passphrase):
    credentials = db.credentials()
    if credentials:
        with GPG(config.path) as gpg:
            # decrypt passwords
            for cred in credentials:
                cred["password"] = gpg.decrypt(cred["password"], passphrase)

            # recreate keys if exists
            if db.has_keys():
                new_passphrase = click.prompt('New passphrase',
                                              hide_input=True,
                                              confirmation_prompt=True)
                create_keys(new_passphrase)

            # encrypt passwords
            for cred in credentials:
                cred["password"] = gpg.encrypt(cred["password"])

        # remove old and insert re-encrypted credentials
        db.purge()
        db.insert_multiple(credentials)

        # commit
        repo = Repository(db.path)
        repo.commit(message='Reset database')


@cli.command(help='Shows passpie database changes history')
@click.option("--init", is_flag=True, help="Enable history tracking")
@click.option("--reset-to", default=-1, help="Undo changes in database")
@pass_db
def log(db, reset_to, init):
    repo = Repository(db.path)
    if reset_to >= 0:
        repo.reset(reset_to)
    elif init:
        repo.init()
    else:
        commits = []
        for number, message in enumerate(repo.commit_list()):
            number = click.style(str(number), fg='magenta')
            message = message.strip()
            commits.append("[{}] {}".format(number, message))

        for commit in reversed(commits):
            print(commit)
