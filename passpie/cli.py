from functools import wraps
import json
import logging
import os
import shutil
import sys

import click
import yaml

from . import clipboard, completion, config, checkers, importers
from .crypt import create_keys, encrypt, decrypt
from .database import Database
from .table import Table
from .utils import genpass, ensure_dependencies
from .history import clone
from .validators import validate_config, validate_cols, validate_remote


__version__ = "1.5.5"
pass_db = click.make_pass_decorator(Database, ensure=False)


def ensure_passphrase(passphrase, config):
    encrypted = encrypt('OK', recipient=config['recipient'], homedir=config['homedir'])
    decrypted = decrypt(encrypted,
                        recipient=config['recipient'],
                        passphrase=passphrase,
                        homedir=config['homedir'])
    if not decrypted == 'OK':
        message = "Wrong passphrase"
        message_full = u"Wrong passphrase for recipient: {} in homedir: {}".format(
            config['recipient'],
            config['homedir'],
        )
        logging.debug(message_full)
        raise click.ClickException(click.style(message, fg='red'))


def logging_exception(exceptions=[Exception]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (click.ClickException, click.Abort):
                raise
            except tuple(exceptions) as e:
                logging_level = logging.getLogger().getEffectiveLevel()
                if logging_level == logging.DEBUG:
                    raise
                elif logging_level == logging.CRITICAL:
                    pass
                else:
                    logging.error(str(e))
                sys.exit(1)
        return wrapper
    return decorator


class AliasGroup(click.Group):

    def get_command(self, ctx, name):
        cmd = super(AliasGroup, self).get_command(ctx, name)
        aliases = ctx.params.get('configuration', {}).get('aliases', {})
        if cmd:
            return cmd
        elif name in aliases:
            aliased_name = aliases[name]
            cmd = super(AliasGroup, self).get_command(ctx, aliased_name)
            return cmd


@click.group(cls=AliasGroup, invoke_without_command=True)
@click.option('-D', '--database', 'path', help='Database path or url to remote repository',
              envvar="PASSPIE_DATABASE")
@click.option('--autopull', help='Autopull changes from remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPULL")
@click.option('--autopush', help='Autopush changes to remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPUSH")
@click.option('--config', 'configuration', help='Path to configuration file',
              callback=validate_config, type=click.Path(readable=True, exists=True),
              envvar="PASSPIE_CONFIG")
@click.option('-v', '--verbose', help='Activate verbose output', count=True,
              envvar="PASSPIE_VERBOSE")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, path, autopull, autopush, configuration, verbose):
    try:
        ensure_dependencies()
    except RuntimeError as e:
        raise click.ClickException(click.style(str(e), fg='red'))

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

    if ctx.invoked_subcommand is None:
        ctx.invoke(cli.commands['list'])


@cli.command(help='Generate completion scripts for shells')
@click.argument('shell_name', type=click.Choice(completion.SHELLS),
                default=None, required=False)
@logging_exception()
@pass_db
@click.pass_context
def complete(ctx, db, shell_name):
    commands = cli.commands.keys()
    script = completion.script(shell_name, db.path, commands)
    click.echo(script)


@cli.command(name='list')
@logging_exception()
@pass_db
def list_database(db):
    """Print credential as a table"""
    credentials = db.credentials()
    if credentials:
        table = Table(
            db.config['headers'],
            table_format=db.config['table_format'],
            colors=db.config['colors'],
            hidden=db.config['hidden'],
            hidden_string=db.config['hidden_string'],
        )
        click.echo(table.render(credentials))


@cli.command(name="config")
@click.argument('level', type=click.Choice(['global', 'local', 'current']),
                default='current', required=False)
@logging_exception()
@pass_db
def check_config(db, level):
    """Show current configuration for shell"""
    if level == 'global':
        configuration = config.read(config.HOMEDIR, '.passpierc')
    elif level == 'local':
        configuration = config.read(os.path.join(db.path))
    elif level == 'current':
        configuration = db.config

    if configuration:
        click.echo(yaml.safe_dump(configuration, default_flow_style=False))


@cli.command(help="Initialize new passpie database")
@click.option('-f', '--force', is_flag=True, help="Force overwrite database")
@click.option('-r', '--recipient', help="Keyring default recipient")
@click.option('-c', '--clone', 'clone_repo', help="Clone a remote repository")
@click.option('--no-git', is_flag=True, help="Don't create a git repository")
@click.option('--passphrase', help="Database passphrase")
@logging_exception()
@pass_db
def init(db, force, clone_repo, recipient, no_git, passphrase):
    if force:
        if os.path.isdir(db.path):
            shutil.rmtree(db.path)
            logging.info('removed directory %s' % db.path)
        elif os.path.isfile(db.path):
            os.remove(db.path)
            logging.info('removed file %s' % db.path)

    try:
        if clone_repo and not config.is_repo_url(db.path):
            if config.is_repo_url(clone_repo):
                clone(clone_repo, db.path)
            else:
                message = u"url is not a remote repo: {}".format(clone_repo)
                raise click.ClickException(click.style(message, fg='red'))
        else:
            os.makedirs(db.path)
    except (SystemError, OSError):
        message = u"Path exists '{}'. `--force` to overwrite".format(db.path)
        raise click.ClickException(click.style(message, fg='red'))

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
@click.option('-i', '--interactive', is_flag=True, help="Interactively edit credential")
@click.option('-C', '--copy', is_flag=True, help="Copy password to clipboard")
@logging_exception()
@pass_db
def add(db, fullname, password, random, pattern, interactive, comment, force, copy):
    if random or pattern:
        pattern = pattern if pattern else db.config['genpass_pattern']
        password = genpass(pattern=pattern)
    elif not password:
        password = click.prompt('Password [empty]',
                                hide_input=True,
                                confirmation_prompt=True,
                                show_default=False,
                                default="")

    found = db.credential(fullname=fullname)
    if found and not force:
        message = u"Credential {} already exists. --force to overwrite".format(
            fullname)
        raise click.ClickException(click.style(message, fg='yellow'))

    encrypted = encrypt(password, recipient=db.config['recipient'], homedir=db.config['homedir'])
    db.add(fullname=fullname, password=encrypted, comment=comment)

    if interactive:
        click.edit(filename=db.filename(fullname))

    if copy:
        clipboard.copy(password)
        click.secho('Password copied to clipboard', fg='yellow')

    message = u'Added {}{}'.format(fullname, ' [--force]' if force else '')
    db.repo.commit(message=message)


@cli.command(help="Copy credential password to clipboard/stdout")
@click.argument("fullname")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@click.option("--to", default='clipboard',
              type=click.Choice(['stdout', 'clipboard']),
              help="Copy password destination")
@click.option("--clear", default=0, help="Automatically clear password from clipboard")
@logging_exception()
@pass_db
def copy(db, fullname, passphrase, to, clear):
    ensure_passphrase(passphrase, db.config)
    clear = clear if clear else db.config['copy_timeout']
    credential = db.credential(fullname)
    if not credential:
        message = u"Credential '{}' not found".format(fullname)
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
@click.option('-i', '--interactive', is_flag=True, help="Interactively edit credential")
@click.option('-P', '--pattern', help="Random password regex pattern")
@logging_exception()
@pass_db
def update(db, fullname, name, login, password, random, interactive, pattern, comment):
    credential = db.credential(fullname)
    if not credential:
        message = u"Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    if random or pattern:
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
            encrypted = encrypt(values["password"],
                                recipient=db.config['recipient'],
                                homedir=db.config['homedir'])
            values['password'] = encrypted
        db.update(fullname=fullname, values=values)
        if interactive:
            click.edit(filename=db.filename(fullname))
        db.repo.commit(u'Updated {}'.format(credential['fullname']))


@cli.command(help="Remove credential")
@click.argument("fullname")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@logging_exception()
@pass_db
def remove(db, fullname, yes):
    credentials = db.credentials(fullname=fullname)

    if credentials:
        if not yes:
            creds = ', '.join([c['fullname'] for c in credentials])
            click.confirm(
                u'Remove credentials: ({})'.format(
                    click.style(creds, 'yellow')),
                abort=True
            )
        for credential in credentials:
            db.remove(credential['fullname'])

        fullnames = ', '.join(c['fullname'] for c in credentials)
        db.repo.commit(u'Removed {}'.format(fullnames))


@cli.command(help="Search credentials by regular expressions")
@click.argument("regex")
@logging_exception()
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
@logging_exception()
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
@click.argument("filepath", type=click.Path(readable=True, exists=True))
@click.option("-I", "--importer", type=click.Choice(importers.get_names()),
              help="Specify an importer")
@click.option("--cols", help="CSV expected columns", callback=validate_cols)
@pass_db
def import_database(db, filepath, importer, cols):
    if cols:
        importer = importers.get(name='csv')
        kwargs = {'cols': cols}
    else:
        importer = importers.find_importer(filepath)
        kwargs = {}

    if importer:
        credentials = importer.handle(filepath, **kwargs)
        for cred in credentials:
            encrypted = encrypt(cred['password'],
                                recipient=db.config['recipient'],
                                homedir=db.config['homedir'])
            cred['password'] = encrypted
        db.insert_multiple(credentials)
        db.repo.commit(message=u'Imported credentials from {}'.format(filepath))


@cli.command(name="export", help="Export credentials in plain text")
@click.argument("filepath", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@logging_exception()
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
@logging_exception()
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
@logging_exception()
@pass_db
def purge(db, yes):
    if db.credentials():
        if not yes:
            alert = u"Purge '{}' credentials".format(len(db.credentials()))
            yes = click.confirm(click.style(alert, 'yellow'), abort=True)
        if yes:
            db.purge()
            db.repo.commit(message='Purged database')


@cli.command(help='Shows passpie database changes history')
@click.option("--init", is_flag=True, help="Enable history tracking")
@click.option("--reset-to", default=-1, help="Undo changes in database")
@logging_exception()
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
            commits.append(u"[{}] {}".format(number, message))

        for commit in reversed(commits):
            print(commit)
