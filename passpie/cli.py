import json
import logging
import os
import shutil

import click
from click.decorators import Group
import yaml

from . import clipboard, completion, config, checkers, importers
from .crypt import create_keys, encrypt, decrypt
from .database import Database, is_repo_url
from .table import Table
from .utils import genpass, ensure_dependencies
from .history import clone


__version__ = "1.0.2"
pass_db = click.make_pass_decorator(Database)


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


def ensure_passphrase(passphrase, config):
    encrypted = encrypt('OK', recipient=config['recipient'], homedir=config['homedir'])
    decrypted = decrypt(encrypted,
                        recipient=config['recipient'],
                        passphrase=passphrase,
                        homedir=config['homedir'])
    if not decrypted == 'OK':
        message = "Wrong passphrase"
        message_full = "Wrong passphrase for recipient: {} in homedir: {}".format(
            config['recipient'],
            config['homedir'],
        )
        logging.error(message_full)
        raise click.ClickException(click.style(message, fg='red'))


def validate_remote(ctx, param, value):
    if value:
        try:
            remote, branch = value.split('/')
            return (remote, branch)
        except ValueError:
            raise click.BadParameter('remote need to be in format <remote>/<branch>')


@click.group(invoke_without_command=True,
             cls=AliasedGroup if config.load()['short_commands'] else Group)
@click.option('-D', '--database', help='Database path or url to remote repository',
              envvar="PASSPIE_DATABASE")
@click.option('--autopull', help='Autopull changes from remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPULL")
@click.option('--autopush', help='Autopush changes to remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPUSH")
@click.option('-v', '--verbose', help='Activate verbose output', count=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, autopull, autopush, verbose):
    try:
        ensure_dependencies()
    except RuntimeError as e:
        raise click.ClickException(click.style(str(e), fg='red'))

    # Override configuration
    config_overrides = {}
    if database:
        config_overrides['path'] = clone(url=database) if is_repo_url(database) else database
    if autopush:
        config_overrides['autopush'] = autopush
    if autopull:
        config_overrides['autopull'] = autopull

    # Setup configuration
    configuration = config.load(**config_overrides)

    # Setup database
    db = Database(configuration)
    ctx.obj = db

    # Verbose
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose > 1:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.CRITICAL
    logging.basicConfig(format="%(levelname)s:passpie.%(module)s:%(message)s",
                        level=logging_level)

    # List credentials
    if ctx.invoked_subcommand is None:
        credentials = db.credentials()
        if credentials:
            table = Table(
                configuration['headers'],
                table_format=configuration['table_format'],
                colors=configuration['colors'],
                hidden=['password']
            )
            click.echo(table.render(credentials))


@cli.command(help='Generate completion scripts for shells')
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
@click.option('--passphrase', help="Database passphrase")
@pass_db
def init(db, force, no_git, recipient, passphrase):
    if force:
        if os.path.isdir(db.path):
            shutil.rmtree(db.path)
            logging.info('removed directory %s' % db.path)
        elif os.path.isfile(db.path):
            os.remove(db.path)
            logging.info('removed file %s' % db.path)

    try:
        os.makedirs(db.path)
    except SystemError:
        message = "Path exists '{}'. `--force` to overwrite".format(db.path)
        raise click.ClickException(click.style(message, fg='yellow'))

    if recipient:
        logging.info('create .passpierc file at %s' % db.path)
        config.create(db.path, defaults=dict(recipient=recipient))
    else:
        logging.info('create .passpierc file at %s' % db.path)
        config.create(db.path, defaults={})
        if not passphrase:
            passphrase = click.prompt('Passphrase',
                                      hide_input=True,
                                      confirmation_prompt=True)
        keys_filepath = os.path.join(db.config['path'], '.keys')
        create_keys(passphrase, keys_filepath, key_length=db.config['key_length'])

    if not no_git:
        logging.info('init git repository in %s' % db.path)
        db.repo.init()
        db.repo.commit(message='Initialized git repository', add=True)

    click.echo("Initialized database in {}".format(db.path))


@cli.command(help='Add new credential to database')
@click.argument("fullname")
@click.option('-p', '--password', help="Credential password")
@click.option('-r', '--random', is_flag=True, help="Randonly generate password")
@click.option('-P', '--pattern', help="Random password regex pattern")
@click.option('-c', '--comment', default="", help="Credential comment")
@click.option('-f', '--force', is_flag=True, help="Force overwriting")
@click.option('-C', '--copy', is_flag=True, help="Copy password to clipboard")
@pass_db
def add(db, fullname, password, random, pattern, comment, force, copy):
    if random:
        pattern = pattern if pattern else db.config['genpass_pattern']
        password = genpass(pattern=pattern)
    elif not password:
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)

    found = db.credential(fullname=fullname)
    if found and not force:
        message = "Credential {} already exists. --force to overwrite".format(
            fullname)
        raise click.ClickException(click.style(message, fg='yellow'))

    encrypted = encrypt(password, recipient=db.config['recipient'], homedir=db.config['homedir'])
    db.add(fullname=fullname, password=encrypted, comment=comment)

    if copy:
        clipboard.copy(password)
        click.secho('Password copied to clipboard', color='yellow')

    message = 'Added {}{}'.format(fullname, ' [--force]' if force else '')
    db.repo.commit(message=message)


@cli.command(help="Copy credential password to clipboard/stdout")
@click.argument("fullname")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@click.option("--to", default='clipboard',
              type=click.Choice(['stdout', 'clipboard']),
              help="Copy password destination")
@click.option("--clear", default=0, help="Automatically clear password from clipboard")
@pass_db
def copy(db, fullname, passphrase, to, clear):
    ensure_passphrase(passphrase, db.config)
    clear = clear if clear else db.config['copy_timeout']
    credential = db.credential(fullname)
    if not credential:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    encrypted = credential["password"]
    decrypted = decrypt(encrypted,
                        recipient=db.config['recipient'],
                        passphrase=passphrase,
                        homedir=db.config['homedir'])
    if to == 'clipboard':
        clipboard.copy(decrypted, clear)
        if not clear:
            click.secho('Password copied to clipboard', fg='yellow')
    elif to == 'stdout':
        click.echo(decrypted)


@cli.command(help="Update credential")
@click.argument("fullname")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.option("--comment", help="Credential new comment")
@click.option("--password", help="Credential new password")
@click.option('--random', is_flag=True, help="Credential new randomly generated password")
@click.option('-P', '--pattern', help="Random password regex pattern")
@pass_db
def update(db, fullname, name, login, password, random, pattern, comment):
    credential = db.credential(fullname)
    if not credential:
        message = "Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    if random:
        pattern = pattern if pattern else db.config['genpass_pattern']
        password = genpass(pattern=pattern)

    values = credential.copy()
    if any([name, login, password, random, comment]):
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
            encrypted = encrypt(password, recipient=db.config['recipient'], homedir=db.config['homedir'])
            values['password'] = encrypted
        db.update(fullname=fullname, values=values)
        db.repo.commit('Updated {}'.format(credential['fullname']))


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
        db.repo.commit('Removed {}'.format(fullnames))


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
    ensure_passphrase(passphrase, db.config)
    credentials = db.credentials()

    for cred in credentials:
        decrypted = decrypt(cred['password'],
                            recipient=db.config['recipient'],
                            passphrase=passphrase,
                            homedir=db.config['homedir'])
        cred["password"] = decrypted

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
        for cred in credentials:
            encrypted = encrypt(cred['password'], recipient=db.config['recipient'], homedir=db.config['homedir'])
            cred['password'] = encrypted
        db.insert_multiple(credentials)

        db.repo.commit(message='Imported credentials from {}'.format(filepath))


@cli.command(name="export", help="Export credentials in plain text")
@click.argument("filepath", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@pass_db
def export_database(db, filepath, as_json, passphrase):
    ensure_passphrase(passphrase, db.config)
    credentials = db.all()

    for cred in credentials:
        decrypted = decrypt(cred['password'],
                            recipient=db.config['recipient'],
                            passphrase=passphrase,
                            homedir=db.config['homedir'])
        cred["password"] = decrypted

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
    ensure_passphrase(passphrase, db.config)
    credentials = db.credentials()
    if credentials:
        # decrypt all credentials
        for cred in credentials:
            decrypted = decrypt(cred['password'],
                                recipient=db.config['recipient'],
                                passphrase=passphrase,
                                homedir=db.config['homedir'])
            cred["password"] = decrypted

        # recreate keys if exists
        if db.has_keys():
            new_passphrase = click.prompt('New passphrase',
                                          hide_input=True,
                                          confirmation_prompt=True)
            create_keys(new_passphrase)

        # encrypt passwords
        for cred in credentials:
            cred['password'] = encrypt(cred['password'],
                                       recipient=db.config['recipient'],
                                       homedir=db.config['homedir'])

        # remove old and insert re-encrypted credentials
        db.purge()
        db.insert_multiple(credentials)

        # commit
        db.repo.commit(message='Reset database')


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
            db.repo.commit(message='Purged database')


@cli.command(help='Shows passpie database changes history')
@click.option("--init", is_flag=True, help="Enable history tracking")
@click.option("--reset-to", default=-1, help="Undo changes in database")
@pass_db
def log(db, reset_to, init):
    if reset_to >= 0:
        logging.info('reset database to index %s', reset_to)
        db.repo.reset(reset_to)
    elif init:
        db.repo.init()
        db.repo.commit(message='Initialized git repository', add=True)
    else:
        commits = []
        for number, message in enumerate(db.repo.commit_list()):
            number = click.style(str(number), fg='magenta')
            message = message.strip()
            commits.append("[{}] {}".format(number, message))

        for commit in reversed(commits):
            print(commit)
