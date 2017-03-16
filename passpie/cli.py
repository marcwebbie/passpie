# -*- coding: utf-8 -*-
from copy import deepcopy
from tempfile import mkdtemp, NamedTemporaryFile
import csv
import functools
import json
import logging
import os
import sys
import shutil


from tabulate import tabulate
from tinydb.storages import touch
from tinydb import Query
import click

from . import importers
from .config import Config
from .database import (
    Database,
    CredentialFactory,
    split_fullname,
    make_fullname
)
from .gpg import generate_keys, GPG
from .proc import run
from .utils import (
    auto_archive,
    copy_to_clipboard,
    genpass,
    logger,
    mkdir,
    make_archive,
    safe_join,
    which,
    yaml_dump,
    yaml_to_python,
)
from .git import Repo


__version__ = "2.0"


#############################
# table
#############################

class Table(object):

    def __init__(self, config):
        self.table_format = config["TABLE_FORMAT"]
        self.show_password = config["TABLE_SHOW_PASSWORD"]
        self.hidden_string = config["TABLE_HIDDEN_STRING"]
        self.style = config["TABLE_STYLE"]
        self.fields = config["TABLE_FIELDS"]

    def colorize(self, data):
        for field, style in self.style.items():
            for elem in data:
                elem[field] = click.style(elem[field], **style)
        return data

    def hide_password(self, data):
        for elem in data:
            elem["password"] = self.hidden_string
        return data

    def render(self, data):
        data = deepcopy(data)
        data = self.colorize(data)
        if not self.show_password:
            data = self.hide_password(data)
        ordered_data = []
        for elem in data:
            ordered_data.append(tuple(elem[f] for f in self.fields))
        headers = tuple(click.style(f.title(), bold=True) for f in self.fields)
        return tabulate(
            ordered_data,
            headers=headers,
            tablefmt=self.table_format,
            numalign="left",
        )


#############################
# cli
#############################

def prompt_passphrase(db, confirm):
    stdin_text = None
    if not sys.stdin.isatty():
        with click.get_binary_stream("stdin") as stdinfd:
            stdin_text = stdinfd.read().strip()

    if stdin_text:
        passphrase = stdin_text
    else:
        passphrase = click.prompt(
            "Passphrase",
            hide_input=True,
            confirmation_prompt=confirm)
    try:
        db.gpg.ensure()
    except ValueError:
        raise click.ClickException("Wrong passphrase")
    return passphrase


def pass_database(ensure_passphrase=False, confirm_passphrase=False, ensure_exists=True, sync=True):
    def decorator(command):
        @functools.wraps(command)
        def wrapper(*args, **kwargs):
            context = click.get_current_context()
            passphrase = context.meta["passphrase"]
            global_config = Config.get_global()
            try:
                with auto_archive(global_config["DATABASE"]) as archive:
                    config_path = safe_join(archive.path, "config.yml")
                    keys_path = safe_join(archive.path, "keys.yml")
                    cfg = Config(config_path)
                    if not passphrase and (ensure_passphrase or cfg["PRIVATE"] is True):
                        passphrase = prompt_passphrase(confirm=confirm_passphrase)
                    gpg = GPG(keys_path, passphrase, cfg["GPG_HOMEDIR"], cfg["GPG_RECIPIENT"])
                    with Database(archive, cfg, gpg) as db:
                        if ensure_passphrase:
                            db.gpg.ensure()
                        return command(db, *args, **kwargs)
            except (IOError, ValueError) as exception:
                if logger.getEffectiveLevel() == logging.DEBUG:
                    raise
                raise click.ClickException("{}".format(exception))
        return wrapper
    return decorator


def validate_cols(ctx, param, value):
    if value:
        try:
            validated = {c: index for index, c in enumerate(value.split(',')) if c}
            for col in ('name', 'login', 'password'):
                assert col in validated
            return validated
        except (AttributeError, ValueError):
            raise click.BadParameter('cols need to be in format col1,col2,col3')
        except AssertionError as e:
            raise click.BadParameter('missing mandatory column: {}'.format(e))


def validate_yaml_str(ctx, param, value):
    if value:
        try:
            yaml_to_python(
                value)
            return value
        except ValueError:
            raise click.BadParameter('not a valid yaml string: {}'.format(value))


def prompt_update(credential, field, hidden=False):
    value = credential[field]
    prompt = "{} [{}]".format(field.title(), "*****" if hidden else value)
    return click.prompt(prompt,
                        hide_input=hidden,
                        confirmation_prompt=hidden,
                        default=value,
                        show_default=False)


@click.group()
@click.option("-P", "--passphrase", help="Database passphrase")
@click.option("-R", "--recipient", help="Database recipient")
@click.option("-D", "--database", help="Database path")
@click.option("-g", "--git-push", help="Autopush git [origin/master]")
@click.option('-v', '--verbose', count=True, help='Activate verbose output', envvar="PASSPIE_VERBOSE")
@click.option('--debug', is_flag=True, help='Activate debug output', envvar="PASSPIE_DEBUG")
@click.version_option(__version__)
@click.pass_context
def cli(ctx, database, passphrase, recipient, git_push, verbose, debug):
    if database:
        os.environ["PASSPIE_DATABASE"] = database
    if git_push:
        os.environ["PASSPIE_GIT_PUSH"] = git_push
    if recipient:
        os.environ["GPG_RECIPIENT"] = recipient
    ctx.meta["passphrase"] = passphrase

    if verbose is 1:
        logger.setLevel(logging.INFO)
    if debug is True or verbose > 1:
        logger.setLevel(logging.DEBUG)


@cli.command()
@click.argument("path", default=".passpie")
@click.option("-P", "--passphrase", help="Database passphrase")
@click.option("-f", "--force", is_flag=True, help="Force initialization")
@click.option("-r", "--recipient", help="Keyring recipient")
@click.option("--key-length", default="4096", type=click.Choice(["1024", "2048", "4096"]), help="Key length")
@click.option("--expire-date", default='0', help="Key expiration date")
@click.option("-ng", "--no-git", is_flag=True, help="Don't initialize a git repo")
@click.pass_context
def init(ctx, path, passphrase, force, recipient, no_git, key_length, expire_date):
    """Initialize database"""
    config = Config.get_global()
    if not passphrase and not recipient:
        passphrase = click.prompt(
            "Passphrase",
            hide_input=True,
            confirmation_prompt=True,
        )

    if os.path.exists(path):
        if force and os.path.isdir(path):
            shutil.rmtree(path)
        elif force and os.path.isfile(path):
            os.remove(path)
        else:
            msg = "Path '{}' exists [--force] to overwrite".format(path)
            raise click.ClickException(msg)

    config_values = {}
    mkdir(path)
    if recipient:
        config_values["RECIPIENT"] = recipient
    else:
        key_values = {
            "key_length": key_length,
            "passphrase": passphrase,
            "expire_date": expire_date,
        }
        keys_content = generate_keys(key_values)
        keys_file_path = safe_join(path, "keys.asc")
        with click.open_file(keys_file_path, "w") as f:
            f.write(keys_content)

    config_file_path = safe_join(path, "config.yml")
    with click.open_file(config_file_path, "w") as f:
        f.write(yaml_dump(config_values))

    credentials_file_path = safe_join(path, "credentials.yml")
    with click.open_file(credentials_file_path, "w") as f:
        f.write(yaml_dump({}))

    if no_git or config["GIT"] is False:
        pass  # Don't create a git repo
    else:
        repo = Repo(path)
        repo.init().commit("Initialize database")


@cli.command(name="list")
@click.argument("grep", required=False)
def listdb(grep):
    """List credentials as table"""
    with Database(path=".passpie") as db:
        if grep:
            query = (Query().login.search(".*{}.*".format(grep)) |
                     Query().name.search(".*{}.*".format(grep)) |
                     Query().comment.search(".*{}.*".format(grep)))
            credentials = db.search(query)
        else:
            credentials = db.all()

        if credentials:
            table = Table(db.cfg)
            click.echo(table.render(credentials))


@cli.command(name="config")
@click.argument("name", required=False, type=str)
@click.argument("value", required=False, type=str, callback=validate_yaml_str)
def config_database(name, value):
    """Print configuration"""
    with Database(path=".passpie") as db:
        name = name.upper() if name else ""
        if name and name in db.cfg.keys():
            if value:
                db.cfg[name] = yaml_to_python(value)
                db.repo.commit("Set config: {} = {}".format(name, value))
            else:
                click.echo("{}".format(db.cfg[name]))
        else:
            config_content = yaml_dump(dict(db.cfg.data)).strip()
            click.echo(config_content)


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-c", "--comment", default="", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-f", "--force", is_flag=True, help="Force overwrite existing credential")
def add(fullnames, random, comment, password, force):
    """Insert credential"""
    with Database(path=".passpie") as db:
        if random or db.cfg["PASSWORD_RANDOM"]:
            password = genpass(db.cfg["PASSWORD_PATTERN"],
                               db.cfg["PASSWORD_RANDOM_LENGTH"])
        elif password is None:
            password = click.prompt(
                "Password", hide_input=True, confirmation_prompt=True)
        for fullname in fullnames:
            login, name = split_fullname(fullname)
            credential = {
                "name": name,
                "login": login,
                "password": password,
                "comment": comment,
            }
            if db.contains(db.query(fullname)):
                if force:
                    db.update(db.gpg.encrypt(credential), db.query(fullname))
                else:
                    msg = "Credential {} exists. `--force` to overwrite".format(fullname)
                    raise click.ClickException(msg)
            else:
                credential['password'] = db.gpg.encrypt(credential['password'])
                db.insert(credential)

    db.repo.commit("Add credentials '{}'".format((", ").join(fullnames)))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompt")
@click.option("-A", "--all", "purge", is_flag=True, help="Purge all credentials")
def remove(fullnames, force, purge):
    """Remove credential"""
    with Database(path=".passpie") as db:
        if purge:
            db.purge()
            db.repo.commit("Purge credentials")
        else:
            removed = False
            fulnames = [f for f in fullnames if db.contains(db.query(f))]
            for fullname in fulnames:
                if force or click.confirm("Remove {}".format(fullname)):
                    db.remove(db.query(fullname))
                    removed = True
            if removed is True:
                msg = "Remove credentials '{}'".format((", ").join(fullnames))
                db.repo.commit(msg)


def passphrase_callback(ctx, param, val):
    return ctx.meta['passphrase'] or val


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-P", "--pattern", help="Random password pattern")
@click.option("-C", "--copy", is_flag=True, help="Copy passwor to clipboard")
@click.option("-i", "--interactive", is_flag=True, help="Interactive confirm updates")
@click.option("-c", "--comment", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-l", "--login", help="Credentials login")
@click.option("-n", "--name", help="Credentials name")
@click.option("-P", "--passphrase", callback=passphrase_callback)
@click.pass_context
def update(ctx, passphrase, fullnames, random, pattern, copy, comment, password, name, login, interactive):
    """Update credential"""
    with Database(".passpie") as db:
        updated = []
        for fullname in [f for f in fullnames if db.contains(db.query(f))]:
            if interactive is True and not click.confirm("Update {}".format(fullname)):
                # Don't update
                continue
            cred = db.get(db.query(fullname))
            values = {}
            if login:
                values["login"] = login
            if name:
                values["name"] = name
            if password:
                values["password"] = db.gpg.encrypt(password)
            if comment:
                values["comment"] = comment
            if random:
                values["password"] = genpass(pattern or db.config["PASSWORD_PATTERN"])

            if not values:
                values["login"] = prompt_update(cred, "login")
                values["name"] = prompt_update(cred, "name")
                values["password"] = prompt_update(cred, "password", hidden=True)
                values["comment"] = prompt_update(cred, "comment")

            db.update(values, db.query(fullname))
            updated.append(fullname)

        if updated:
            db.repo.commit("Update credentials '{}'".format((", ").join(fullnames)))

            if copy:
                if not passphrase:
                    passphrase = click.prompt("Passphrase", hide_input=True)
                password = db.gpg.decrypt(cred["password"], passphrase)
                copy_to_clipboard(password, db.cfg["COPY_TIMEOUT"])


@cli.command()
@click.argument("fullname")
@click.argument("dest", type=click.File("w"), required=False)
@click.option("-t", "--timeout", type=int, default=0, help="Timeout to clear clipboard")
@pass_database(ensure_passphrase=True)
def copy(db, fullname, dest, timeout):
    """Copy credential password"""
    credential = db.get(db.query(fullname))
    timeout = timeout or db.config["COPY_TIMEOUT"]
    if credential:
        credential = db.decrypt(credential)
        password = credential["password"]
        if dest:
            dest.write(password)
        else:
            copy_to_clipboard(password, timeout)
    else:
        raise click.ClickException("{} not found".format(fullname))


@cli.command(name="import")
@click.argument("filepath", required=False, type=click.Path(readable=True, exists=True, allow_dash=True))
@click.option("-I", "--importer", type=click.Choice(importers.get_names()),
              help="Specify an importer")
@click.option("--csv", help="CSV expected columns", callback=validate_cols)
@click.option("--skip-lines", type=int, help="Number of lines to skip")
@click.option("-f", "--force", is_flag=True, help="Force importing credentials")
@pass_database()
def import_database(db, filepath, importer, csv, force, skip_lines):
    """Import credentials in plain text"""
    tempfile = None
    if filepath is None or filepath == "-":
        tempfile = NamedTemporaryFile()
        with open(tempfile.name, "w") as stdinfile:
            stdinfile.write(click.get_text_stream('stdin').read())
        filepath = tempfile.name

    if csv:
        importer = importers.get(name='csv')
        params = {'cols': csv, 'skip_lines': skip_lines}
    else:
        importer = importers.find_importer(filepath)
        params = {}

    if importer:
        imported = False
        credentials = importer.handle(filepath, params=params)
        for credential in [db.encrypt(c) for c in credentials]:
            fullname = make_fullname(credential["login"], credential["name"])
            if db.contains(db.query(fullname)):
                if force is False and not click.confirm("Update {}".format(fullname)):
                    continue
                else:
                    db.update(credential, db.query(fullname))
                    imported = True
            else:
                db.insert(credential)
                imported = True

        if imported is True:
            if tempfile:
                message = 'Imported credentials from stdin'
            else:
                message = u'Imported credentials from {}'.format(filepath)
            db.repo.commit(message=message)


@cli.command(name="export")
@click.argument("exportfile", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@click.option("--csv", "as_csv", is_flag=True, help="Export as CSV")
@pass_database(ensure_passphrase=True, sync=False)
def export_database(db, exportfile, as_json, as_csv):
    """Export credentials in plain text"""
    credentials = [dict(db.decrypt(c)) for c in db.all()]
    if as_csv:
        writer = csv.writer(exportfile)
        writer.writerow(["name", "login", "password", "comment"])
        for cred in credentials:
            row = [cred["name"],
                   cred["login"],
                   cred["password"],
                   cred["comment"]]
            try:
                writer.writerow(row)
            except UnicodeEncodeError:
                writer.writerow([cell.encode("utf-8") for cell in row])
    elif as_json:
        content = json.dumps(credentials, indent=2)
        exportfile.write(content)
    else:
        content = yaml_dump(credentials)
        exportfile.write(content)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
def git(command):
    """Git commands"""
    cmd = ["git"] + list(command)
    run(cmd, cwd=".passpie", pipe=False)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@click.option("--gen-key", is_flag=True, help="Generate keys")
@pass_database()
def gpg(db, command, gen_key):
    """GPG commands"""
    if gen_key:
        # for debbuging values
        # values = {
        #     "name": "Debugger",
        #     "email": "debugger@example.com",
        #     "passphrase": "passphrase2",
        # }
        values = {
            "key_length": click.prompt("Key length", default=4096),
            "name": click.prompt("Name"),
            "email": click.prompt("Email"),
            "comment": click.prompt("Comment", default=""),
            "passphrase": click.prompt("Passphrase", hide_input=True, confirmation_prompt=True),
            "expire_date": click.prompt("Expire date", default=0),
        }
        keys_content = generate_keys(values)
        yaml_dump(db.gpg.keys + [keys_content], db.gpg.path)
    else:
        cmd = [which("gpg2", "gpg"), "--homedir", db.gpg.homedir] + list(command)
        run(cmd, cwd=db.path, pipe=False)
