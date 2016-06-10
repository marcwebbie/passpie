import os
import shutil

import click

from . import config, clipboard
from .database import Database, split_fullname
from .gpg import create_keys
from .table import Table
from .utils import genpass


__version__ = "2.0"
pass_db = click.make_pass_decorator(Database, ensure=True)
pass_cfg = click.make_pass_decorator(dict, ensure=True)


def validate_remote(ctx, param, value):
    if value:
        try:
            remote, branch = value.split('/')
            return (remote, branch)
        except ValueError:
            raise click.BadParameter('remote need to be in format <remote>/<branch>')


@click.group(invoke_without_command=True)
@click.option('-D', '--database', 'db_path',
              help='Database path or url to remote repository',
              envvar="PASSPIE_DATABASE")
@click.option('--passphrase', "-P", help='Global database passphrase',
              envvar="PASSPIE_PASSPHRASE")
@click.option('--autopush', help='Autopush changes to remote pository',
              callback=validate_remote, envvar="PASSPIE_AUTOPUSH")
@click.option('--config', 'config_path', help='Path to configuration file',
              type=click.Path(readable=True, exists=True),
              envvar="PASSPIE_CONFIG")
@click.option('-v', '--verbose', help='Activate verbose output', count=True,
              envvar="PASSPIE_VERBOSE")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, db_path, passphrase, autopush, config_path, verbose):
    extra_config = {}
    if db_path:
        extra_config["path"] = db_path
    if autopush:
        extra_config["autopush"] = autopush
    if passphrase:
        extra_config["passphrase"] = passphrase

    cfg = config.load(extra_config=extra_config)
    if ctx.invoked_subcommand == "init":
        ctx.obj = cfg
    else:
        ctx.obj = Database(cfg)


@cli.command()
@click.option("-f", "--force", is_flag=True, help="Force initialization")
@click.option("-r", "--recipient", help="Keyring recipient")
@pass_cfg
def init(cfg, force, recipient):
    """Initialize database
    Steps to create a passpie database
    1) Create directory for `db.path`
    2) Create keys file if not `recipient`
    3) Create a config file empty if not recipient,
       with recipient if recipient was passed
    """
    if os.path.isdir(cfg["path"]) and not force:
        click.secho("Path '{}' exists [--force] to overwrite".format(cfg["path"]), fg="yellow")
        raise click.Abort("")
    elif os.path.isdir(cfg["path"]):
        shutil.rmtree(cfg["path"])

    overrides = {}
    if recipient:
        overrides["recipient"] = recipient
    else:
        create_keys(cfg["passphrase"], os.path.join(cfg["path"], ".keys"))
    config.create(os.path.join(cfg["path"], ".config"), overrides={"recipient": recipient})


@cli.command()
@click.argument("fullnames", nargs=-1)
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-c", "--comment", is_flag=True, help="Credential comment")
@pass_db
def add(db, fullnames, random, comment):
    for fullname in fullnames:
        login, name = split_fullname(fullname)
        if random:
            password = genpass(db.cfg["genpass_pattern"])
        credential = {
            "name": name,
            "login": login,
            "password": password,
            "comment": comment,
        }
        db.insert(db.encrypt_fields(credential))


@cli.command(name='list')
@pass_db
def list_db(db):
    """Print credential as a table"""
    credentials = db.all()
    if credentials:
        table = Table(
            db.cfg['headers'],
            table_format=db.cfg['table_format'],
            colors=db.cfg['colors'],
            hidden=db.cfg['hidden'],
            hidden_string=db.cfg['hidden_string'],
        )
        click.echo(table.render(credentials))


@cli.command()
@click.argument("fullname")
@pass_db
def copy(db, fullname):
    """Copy credential password"""
    credential = db.get(db.query(fullname))
    if credential:
        clipboard.copy(db.gpg.decrypt(credential["password"]))
