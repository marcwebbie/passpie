from functools import wraps
import json
import logging
import os
import shutil
import sys

import click
import yaml

from passpie import config, database, table, clipboard, completion, importers
from .callbacks import validate_remote
from .utils import genpass
from .crypt import GPG, create_keys, ensure_keys
from .database import split_fullname
from .termui import (
    pass_context_object,
    password_prompt,
    ensure_passphrase,
    validate_cols,
)

__version__ = "1.4.1"


def logging_exception(exceptions=[Exception]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (click.ClickException, click.Abort):
                raise
            except tuple(exceptions) as e:
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                    raise
                logging.error(str(e))
                sys.exit(1)
        return wrapper
    return decorator


@click.group(invoke_without_command=True)
@click.option('-D', '--database', 'db_path',
              help='Database path or url to remote repository',
              envvar="PASSPIE_DATABASE")
@click.option('--passphrase', "-P", help='Global database passphrase',
              envvar="PASSPIE_PASSPHRASE")
@click.option('--autopull', help='Autopull changes from remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPULL")
@click.option('--autopush', help='Autopush changes to remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPUSH")
@click.option('--config', 'config_path', help='Path to configuration file',
              type=click.Path(readable=True, exists=True),
              envvar="PASSPIE_CONFIG")
@click.option('-v', '--verbose', help='Activate verbose output', count=True,
              envvar="PASSPIE_VERBOSE")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, db_path, passphrase, autopull, autopush, config_path, verbose):
    overrides = {}
    if db_path:
        config_path = db_path
        overrides = {"path": db_path}

    ctx.config = config.from_path(config_path, overrides=overrides)
    ctx.database = database.Database(ctx.config['path'])
    ctx.database.passphrase = passphrase
    ctx.gpg = GPG.build(
        ctx.database.path,
        fallback_recipient=ctx.config['recipient'],
        fallback_homedir=ctx.config['recipient'],
    )

    if ctx.invoked_subcommand is None:
        ctx.invoke(list_database)


@cli.command(name="list")
@pass_context_object('config', 'cfg')
@pass_context_object('database', 'db')
def list_database(db, cfg):
    credentials = sorted(db.all(), key=lambda e: (e['name'], e['login']))
    cred_table = table.Table(
        headers=cfg['headers'],
        table_format=cfg['table_format'],
        colors=cfg['colors'],
        hidden=cfg['hidden'],
        hidden_string=cfg['hidden_string'],
    )
    click.echo(cred_table.render(data=credentials))


@cli.command(help='Generate completion scripts for shells')
@click.argument('shell_name', type=click.Choice(completion.SHELLS),
                default=None, required=False)
@pass_context_object('database', 'db')
def complete(db, shell_name):
    commands = cli.commands.keys()
    script = completion.script(shell_name, db.path, commands)
    click.echo(script)


@cli.command(name="config")
@click.argument('level', type=click.Choice(['global', 'local', 'current']),
                default='current', required=False)
@pass_context_object('database', 'db')
@pass_context_object('config', 'configuration')
def check_config(configuration, db, level):
    """Show current configuration for shell"""
    if level == 'global':
        configuration = config.from_path(config.DEFAULT_CONFIG_PATH)
    elif level == 'local':
        configuration = config.from_path(os.path.join(db.path))
    if configuration:
        click.echo(yaml.dump(configuration, default_flow_style=False))


@cli.command(help="Initialize new passpie database")
@click.option('-f', '--force', is_flag=True, help="Force overwrite database")
@click.option('-r', '--recipient', help="Keyring default recipient")
@click.option('-c', '--clone', 'clone_repo', help="Clone a remote repository")
@click.option('--no-git', is_flag=True, help="Don't create a git repository")
@click.option('--passphrase', help="Database passphrase")
@pass_context_object('database', 'db')
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
@pass_context_object('config', 'cfg')
@pass_context_object('database', 'db')
@pass_context_object('gpg', 'gpg')
@click.pass_context
def add(ctx, cfg, db, gpg, fullname, password, random, pattern, interactive, comment, force, copy):
    """Add new credential"""
    if random or pattern:
        pattern = pattern if pattern else cfg['genpass_pattern']
        password = genpass(pattern)
    elif not password:
        password = password_prompt()

    login, name = split_fullname(fullname)
    credential = {"name": name, "login": login, "password": password, "comment": comment}

    for field in (f for f in cfg['encrypted'] if f in credential):
        credential[field] = gpg.encrypt(credential[field])

    db.insert(credential)

    if copy:
        ctx.invoke(cli.commands.get('copy'), fullname=fullname)
    if interactive:
        ctx.invoke(cli.commands.get('edit'), fullname=fullname)

    if interactive:
        click.edit(filename=db.filename(fullname))

    if copy:
        clipboard.copy(password)
        click.secho('Password copied to clipboard', fg='yellow')

    message = u'Added {}{}'.format(fullname, ' [--force]' if force else '')
    db.repo.commit(message=message)


@cli.command(help="Copy credential password to clipboard/stdout")
@click.argument("fullname")
@click.option("--passphrase", "-P", help="Database passphrase")
@click.option("--to", default='clipboard',
              type=click.Choice(['stdout', 'clipboard']),
              help="Copy password destination")
@click.option("--clear", default=0, help="Automatically clear password from clipboard")
@logging_exception()
@pass_context_object('config', 'cfg')
@pass_context_object('database', 'db')
@pass_context_object('gpg', 'gpg')
def copy(gpg, db, cfg, fullname, passphrase, to, clear):
    credential = db.credential(fullname)
    if not credential:
        message = u"Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    if db.passphrase:
        passphrase = db.passphrase
    elif passphrase is None:
        passphrase = click.prompt("Passphrase", hide_input=True)
    ensure_passphrase(passphrase, gpg, cfg)

    clear = clear if clear else cfg['copy_timeout']

    encrypted_password = credential["password"]
    decrypted = gpg.decrypt(encrypted_password, passphrase=passphrase)
    if to == 'clipboard':
        clipboard.copy(decrypted, clear)
        if not clear:
            click.secho('Password copied to clipboard', fg='yellow')
    elif to == 'stdout':
        click.echo(decrypted)


@cli.command()
@click.argument("fullname")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.option("--comment", help="Credential new comment")
@click.option("--password", help="Credential new password")
@click.option('--random', is_flag=True, help="Credential new randomly generated password")
@click.option('-i', '--interactive', is_flag=True, help="Interactively edit credential")
@click.option('-P', '--pattern', help="Random password regex pattern")
@pass_context_object('database', 'db')
@pass_context_object('gpg', 'gpg')
def update(gpg, db, fullname, name, login, password, random, interactive, pattern, comment):
    """Update credential"""
    credential = db.credential(fullname=fullname)
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
            encrypted = gpg.encrypt(password)
            values['password'] = encrypted
        db.update(fields=values, fullname=fullname)
        if interactive:
            click.edit(filename=db.filename(fullname))
        db.repo.commit(u'Updated {}'.format(credential['fullname']))


@cli.command(help="Remove credential")
@click.argument("fullname")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@logging_exception()
@pass_context_object('database', 'db')
def remove(db, fullname, yes):
    credential = db.credential(fullname)
    if not credential:
        message = u"Credential '{}' not found".format(fullname)
        raise click.ClickException(click.style(message, fg='red'))

    removed_credentials = db.search(db.cond(fullname))
    fullnames = ', '.join(c['fullname'] for c in removed_credentials)
    if not yes:
        click.confirm(
            u'Remove credentials: ({})'.format(click.style(fullnames, 'yellow')),
            abort=True
        )
    db.remove(fullname=fullname)
    db.repo.commit(u'Removed {}'.format(fullnames))


@cli.command(help="Search credentials by regular expressions")
@click.argument("regex")
@pass_context_object('config', 'cfg')
@pass_context_object('database', 'db')
def search(db, cfg, regex):
    credentials = sorted(db.matches(regex), key=lambda e: (e['name'], e['login']))
    cred_table = table.Table(
        headers=cfg['headers'],
        table_format=cfg['table_format'],
        colors=cfg['colors'],
        hidden=cfg['hidden'],
        hidden_string=cfg['hidden_string'],
    )
    click.echo(cred_table.render(data=credentials))


@cli.command(help="Diagnose database for improvements")
@click.option("--full", is_flag=True, help="Show all entries")
@click.option("--days", default=90, type=int, help="Elapsed days")
@click.option("--passphrase", prompt="Passphrase", hide_input=True)
@logging_exception()
@pass_context_object('database', 'db')
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
@pass_context_object('database', 'db')
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
@pass_context_object('database', 'db')
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
@click.option("--passphrase", "-P", help="Database passphrase")
@click.option("--new-passphrase", "-N", help="New database passphrase")
@pass_context_object('config', 'cfg')
@pass_context_object('gpg', 'gpg')
@pass_context_object('database', 'db')
def reset(db, gpg, cfg, passphrase, new_passphrase):
    if db.passphrase:
        passphrase = db.passphrase
    elif passphrase is None:
        passphrase = click.prompt("Passphrase", hide_input=True)
    ensure_passphrase(passphrase, gpg, cfg)

    credentials = db.all()
    if credentials:
        # decrypt all credentials
        for cred in credentials:
            decrypted = gpg.decrypt(cred['password'], passphrase=passphrase)
            cred["password"] = decrypted

        # recreate keys if exists
        if ensure_keys(db.path):
            if new_passphrase is None:
                new_passphrase = click.prompt(
                    'New passphrase', hide_input=True, confirmation_prompt=True
                )
            create_keys(new_passphrase, ensure_keys(db.path), cfg['key_length'])

        # encrypt passwords
        for cred in credentials:
            cred['password'] = gpg.encrypt(cred['password'])

        # remove old and insert re-encrypted credentials
        db.purge()
        db.insert_multiple(credentials)

        # commit
        db.repo.commit(message='Reset database')


@cli.command(help='Remove all credentials from database')
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@logging_exception()
@pass_context_object('database', 'db')
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
@pass_context_object('database', 'db')
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
