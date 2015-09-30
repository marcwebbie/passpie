import json
import logging
import os
import shutil

import click
import yaml

from . import clipboard, completion, config, checkers, importers
from .crypt import GPG, create_keys
from .database import Database
from .history import Repository
from .table import Table
from .utils import genpass, mkdir_open


__version__ = "0.3.3"
pass_db = click.make_pass_decorator(Database)


@click.group(invoke_without_command=True)
@click.option('-D', '--database', help='Alternative database path',
              type=click.Path(dir_okay=True, writable=True, resolve_path=True))
@click.option('-v', '--verbose', help='Activate verbose output', count=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, verbose):
    db_config = config.load()
    if database:
        db_config['path'] = database

    db = Database(db_config)
    ctx.obj = db

    if verbose == 1:
        logging_level = logging.INFO
    elif verbose > 1:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.CRITICAL
    logging.basicConfig(format="%(levelname)s:passpie.%(module)s:%(message)s",
                        level=logging_level)

    if ctx.invoked_subcommand is None:
        credentials = db.credentials()
        if credentials:
            table = Table(
                db.config['headers'],
                table_format=db.config['table_format'],
                colors=db.config['colors'],
                hidden=['password']
            )
            click.echo(table.render(credentials))


@cli.command(help='Shows completion scripts')
@click.argument('shell_name', type=click.Choice(completion.SHELLS),
                default=None, required=False)
@click.option('--commands', default=None)
def complete(shell_name, commands):
    commands = ['add', 'copy', 'remove', 'search', 'update']
    script = completion.script(shell_name, config.path, commands)
    click.echo(script)


@cli.command(help="Initialize new passpie database")
@click.option('--force', is_flag=True, help="Force overwrite database")
@click.option('--no-git', is_flag=True, help="Don't create a git repository")
@click.option('--recipient', help="Keyring default recipient")
@pass_db
def init(db, force, no_git, recipient):
    if force:
        if os.path.isdir(db.path):
            shutil.rmtree(db.path)
            logging.info('removed directory %s' % db.path)
        elif os.path.isfile(db.path):
            os.remove(db.path)
            logging.info('removed file %s' % db.path)
    elif os.path.isdir(db.path):
        message = "Path exists '{}'. `--force` to overwrite".format(
            db.path)
        raise click.ClickException(click.style(message, fg='yellow'))

    os.makedirs(db.path)

    if recipient:
        logging.info('create .passpierc file at %s' % db.path)
        config.create(db.path, default=False, recipient=recipient)
    else:
        logging.info('create .passpierc file at %s' % db.path)
        config.create(db.path, default=False, recipient=recipient)
        config.create(db.path, default=False)
        with mkdir_open(os.path.join(db.config['path'], '.keys'), 'w'):
            pass
        passphrase = click.prompt('Passphrase',
                                  hide_input=True,
                                  confirmation_prompt=True)
        create_keys(passphrase, db.config['path'],
                    key_length=db.config['key_length'])

    if not no_git:
        repo = Repository(db.path)
        logging.info('init git repository in %s' % db.path)
        repo.init()
    click.echo("Initialized database in {}".format(db.path))


@cli.command()
@click.argument("fullname")
@click.option('-r', '--random', 'password', is_flag=True)
@click.password_option(help="Credential password")
@click.option('-c', '--comment', default="", help="Credential comment")
@click.option('-f', '--force', is_flag=True, help="Force overwriting")
@click.option('-C', '--copy', is_flag=True, help="Copy password to clipboard")
@pass_db
def add(db, fullname, password, comment, force, copy):
    if password is True:
        password = genpass(db.config['genpass_length'],
                           db.config['genpass_symbols'])

    found = db.credential(fullname=fullname)
    if found and not force:
        message = "Credential {} already exists. --force to overwrite".format(
            fullname)
        raise click.ClickException(click.style(message, fg='yellow'))

    with GPG(db.path, recipient=db.config['recipient']) as gpg:
        encrypted = gpg.encrypt(password)
        db.add(fullname=fullname, password=encrypted, comment=comment)

    if copy:
        clipboard.copy(password)
        click.secho('Password copied to clipboard', color='yellow')

    repo = Repository(db.path)
    message = 'Added {}{}'.format(fullname, ' [--force]' if force else '')
    repo.commit(message=message)


@cli.command(help="Copy credential password to clipboard/stdout")
@click.argument("fullname")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@click.option("--to", default='clipboard',
              type=click.Choice(['stdout', 'clipboard']))
@click.option("--clear", default=0)
@pass_db
def copy(db, fullname, passphrase, to, clear):
    clear = clear if clear else db.config['copy_timeout']
    credential = db.credential(fullname)
    if not credential:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    with GPG(db.path, recipient=db.config['recipient']) as gpg:
        decrypted = gpg.decrypt(credential["password"], passphrase=passphrase)
        if to == 'clipboard':
            clipboard.copy(decrypted, clear)
            click.secho('Password copied to clipboard', fg='yellow')
        elif to == 'stdout':
            click.echo(decrypted)


@cli.command(help="Update credential")
@click.argument("fullname")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.option("--comment", help="Credential new comment")
@click.option("--password", help="Credential new password")
@click.option('--random', 'password', flag_value=genpass(),
              help="Credential new randomly generated password")
@pass_db
def update(db, fullname, name, login, password, comment):
    credential = db.credential(fullname)
    if not credential:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

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
        if values["password"] != credential["password"]:
            with GPG(db.path, recipient=db.config['recipient']) as gpg:
                values["password"] = gpg.encrypt(values['password'])
        db.update(values, fullname)
        repo = Repository(db.path)
        repo.commit('Updated {}'.format(credential['fullname']))


@cli.command(help="Remove credential")
@click.argument("fullname")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@pass_db
def remove(db, fullname, yes):
    credentials = db.credentials(fullname=fullname)

    if credentials:
        if not yes:
            creds = ', '.join([c['fullname'] for c in credentials])
            click.confirm(
                'Remove credentials: ({})'.format(
                    click.style(creds, 'yellow')),
                abort=True
            )
        for credential in credentials:
            db.remove(credential['fullname'])

        fullnames = ', '.join(c['fullname'] for c in credentials)
        repo = Repository(db.path)
        repo.commit('Removed {}'.format(fullnames))


@cli.command(help="Search credentials by regular expressions")
@click.argument("regex")
@pass_db
def search(db, regex):
    credentials = db.matches(regex)
    if credentials:
        table = Table(
            db.config['headers'],
            table_format=db.config['table_format'],
            colors=db.config['colors'],
            hidden=['password']
        )
        click.echo(table.render(credentials))


@cli.command(help="Diagnose database for improvements")
@click.option("--full", is_flag=True, help="Show all entries")
@click.option("--days", default=90, type=int, help="Elapsed days")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@pass_db
def status(db, full, days, passphrase):
    credentials = db.credentials()

    with GPG(db.path, recipient=db.config['recipient']) as gpg:
        for cred in credentials:
            cred["password"] = gpg.decrypt(cred["password"], passphrase)

    if credentials:
        limit = db.config['status_repeated_passwords_limit']
        credentials = checkers.repeated(credentials, limit)
        credentials = checkers.modified(credentials, days)

        for c in credentials:
            if c['repeated']:
                c['repeated'] = click.style(str(c['repeated']), 'red')
            if c['modified']:
                c['modified'] = click.style(str(c['modified']), 'red')

        table = Table(['fullname', 'repeated', 'modified'],
                      table_format=db.config['table_format'],
                      missing=click.style('OK', 'green'))
        click.echo(table.render(credentials))


@cli.command(name="import", help="Import credentials from path")
@click.argument("filepath", type=click.Path())
@pass_db
def import_database(db, filepath):
    importer = importers.find_importer(filepath)
    if importer:
        credentials = importer.handle(filepath)
        with GPG(db.path, recipient=db.config['recipient']) as gpg:
            for cred in credentials:
                encrypted = gpg.encrypt(cred['password'])
                cred['password'] = encrypted
        db.insert_multiple(credentials)

        repo = Repository(db.path)
        repo.commit(message='Imported credentials from {}'.format(filepath))


@cli.command(name="export", help="Export credentials in plain text")
@click.argument("filepath", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@pass_db
def export_database(db, filepath, as_json, passphrase):
    credentials = db.all()

    with GPG(db.path, recipient=db.config['recipient']) as gpg:
        for cred in credentials:
            cred["password"] = gpg.decrypt(cred["password"], passphrase)

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

    filepath.write(content)


@cli.command(help='Renew passpie database and re-encrypt credentials')
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@pass_db
def reset(db, passphrase):
    credentials = db.credentials()
    if credentials:
        with GPG(db.path, recipient=db.config['recipient']) as gpg:
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


@cli.command(help='Remove all credentials from database')
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@pass_db
def purge(db, yes):
    if db.credentials():
        if not yes:
            alert = "Purge '{}' credentials".format(len(db.credentials()))
            yes = click.confirm(click.style(alert, 'yellow'), abort=True)
        if yes:
            db.purge()
            repo = Repository(db.path)
            repo.commit(message='Purged database')


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
