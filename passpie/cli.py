# -*- coding: utf-8 -*-
from contextlib import contextmanager
from copy import deepcopy
from collections import namedtuple, OrderedDict
from subprocess import Popen, PIPE
from tempfile import mkdtemp, NamedTemporaryFile
import errno
import functools
import json
import logging
import os
import re
import shutil
import sys
import time

from tabulate import tabulate
from tinydb import TinyDB, Query
import click
import pyperclip
import rstr
import yaml

from . import importers


#############################
# process
#############################

DEVNULL = open(os.devnull, 'w')


class Proc(Popen):

    def communicate(self, **kwargs):
        if kwargs.get('input') and isinstance(kwargs['input'], basestring):
            kwargs['input'] = kwargs['input'].encode('utf-8')
        return super(Proc, self).communicate(**kwargs)

    def __exit__(self, *args, **kwargs):
        if hasattr(super(Proc, self), '__exit__'):
            super(Proc, self).__exit__(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        if hasattr(super(Proc, self), '__enter__'):
            return super(Proc, self).__enter__(*args, **kwargs)
        return self


def run(*args, **kwargs):
    Response = namedtuple("Response", "cmd std_out std_err returncode")
    data = kwargs.pop('data', None)
    kwargs.setdefault('shell', False)
    kwargs.setdefault('pipe', True)
    kwargs.setdefault('stdin', PIPE)
    if kwargs.pop("pipe") is True:
        kwargs.setdefault('stderr', PIPE)
        kwargs.setdefault('stdout', PIPE)

    with Proc(*args, **kwargs) as proc:
        std_out, std_err = proc.communicate(input=data)
        cmd = args[0]
        returncode = proc.returncode
        try:
            std_out = std_out.decode('utf-8')
            std_err = std_err.decode('utf-8')
        except AttributeError:
            pass
        response = Response(cmd, std_out, std_err, returncode)

    if response.returncode != 0:
        logging.debug("Command error: {}".format(response))
    return response


#############################
# utils
#############################

def safe_join(*paths):
    return os.path.join(*[os.path.expanduser(p) for p in paths])


def yaml_dump(data):
    return yaml.safe_dump(data, default_flow_style=False)


def genpass(pattern):
    """generates a password with random chararcters
    examples:
      cat /dev/urandom | strings

    """
    try:
        return rstr.xeger(pattern)
    except re.error as e:
        raise ValueError(str(e))


def which(binary):
    try:
        from shutil import which as _which
    except ImportError:
        from distutils.spawn import find_executable as _which

    path = _which(binary)
    if path:
        realpath = os.path.realpath(path)
        return realpath
    return None


def copy_to_clipboard(text, timeout):
    pyperclip.copy(text)
    if timeout:
        for dot in ['.' for _ in range(timeout)]:
            sys.stdout.write(dot)
            sys.stdout.flush()
            time.sleep(1)
        else:
            pyperclip.copy("\b")
            print("")


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


@contextmanager
def mkdir_open(path, mode):
    mkdir(os.path.dirname(path))
    with open(path, mode) as fd:
        yield fd


#############################
# configuration
#############################

HOMEDIR = os.path.expanduser("~")
HOMEDIR_CONFIG_PATH = safe_join(HOMEDIR, ".passpierc")
DEFAULT_CONFIG = {
    # Database
    'PATH': safe_join(HOMEDIR, ".passpie"),
    'GIT': True,
    'AUTOPUSH': 'origin/master',
    'ENCRYPTED_FIELDS': ['password'],

    # GPG
    'KEY_LENGTH': 4096,
    'HOMEDIR': os.path.join(os.path.expanduser('~/.gnupg')),
    'RECIPIENT': None,
    'KEYS': {
        'PUBLIC': "",
        'PRIVATE': "",
    },

    # Table
    'TABLE_FORMAT': 'fancy_grid',
    'TABLE_SHOW_PASSWORD': False,
    'TABLE_HIDDEN_STRING': u'********',
    'TABLE_FIELDS': ('name', 'login', 'password', 'comment'),
    'TABLE_STYLE': {
        'login': {"fg": 'green'},
        'name': {"fg": 'yellow'}
    },

    # Credentials
    'COPY_TIMEOUT': 0,
    'PATTERN': "[a-zA-Z0-9=+_*!?&%$# ]{32}",
    'RANDOM': False,
}


def config_from_file(path):
    try:
        with open(path) as f:
            cfg = yaml.safe_load(f.read())
    except IOError:
        logging.debug(u'config file "{}" not found'.format(path))
        return {}
    except yaml.scanner.ScannerError as e:
        logging.error(u'Malformed user configuration file: {}'.format(e))
        return {}
    return cfg or {}


def config_create(path, values={}):
    with open(path, "w") as f:
        f.write(yaml.safe_dump(values, default_flow_style=False))


def config_load(overrides):
    cfg = deepcopy(DEFAULT_CONFIG)
    cfg.update(config_from_file(safe_join(HOMEDIR, ".config")))
    cfg.update(overrides)
    cfg.update(config_from_file(safe_join(cfg["PATH"], ".config")))
    return cfg


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
# gpg
#############################

GPG_HOMEDIR = os.path.expanduser('~/.gnupg')
DEVNULL = open(os.devnull, 'w')
KEY_INPUT = u"""Key-Type: RSA
Key-Length: {}
Subkey-Type: RSA
Name-Comment: Auto-generated by Passpie
Passphrase: {}
Name-Real: Passpie
Name-Email: passpie@local
Expire-Date: 0
%commit
"""


def ensure_keys(path):
    keys_path = safe_join(os.path.expanduser(path), '.keys')
    if os.path.isfile(keys_path):
        return keys_path


def make_key_input(passphrase, key_length):
    passphrase = unicode(passphrase)
    key_length = unicode(key_length)
    key_input = KEY_INPUT.format(key_length, passphrase)
    return key_input


def import_keys(keys_path, homedir):
    command = [
        which('gpg2') or which('gpg'),
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--homedir', homedir,
        '--import', keys_path
    ]
    ret = run(command)
    return ret.std_out


def export_keys(homedir, private=False):
    command = [
        which('gpg2') or which('gpg'),
        '--no-version',
        '--batch',
        '--homedir', homedir,
        '--export-secret-keys' if private else '--export',
        '--armor',
        '-o', '-'
    ]
    ret = run(command)
    return ret.std_out


def create_keys(passphrase, key_length=4096):
    homedir = mkdtemp()
    command = [
        which('gpg2') or which('gpg'),
        '--batch',
        '--no-tty',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--homedir', homedir,
        '--gen-key',
    ]
    key_input = make_key_input(passphrase, key_length)
    run(command, data=key_input)
    return export_keys(homedir), export_keys(homedir, private=True)


def get_default_recipient(homedir, secret=False):
    command = [
        which('gpg2') or which('gpg'),
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--no-mdc-warning',
        '--list-{}-keys'.format('secret' if secret else 'public'),
        '--fingerprint',
        '--homedir', homedir,
    ]
    ret = run(command)
    for line in ret.std_out.splitlines():
        try:
            mobj = re.search(r'(([0-9A-F]{4}\s*?){10})', line)
            fingerprint = mobj.group().replace(' ', '')
            return fingerprint
        except (AttributeError, IndexError):
            continue
    return ''


def encrypt(data, recipient, homedir):
    command = [
        which('gpg2') or which('gpg'),
        '--batch',
        '--no-tty',
        '--always-trust',
        '--armor',
        '--recipient', recipient,
        '--homedir', homedir,
        '--encrypt'
    ]
    ret = run(command, data=data)
    return ret.std_out


def decrypt(data, recipient, homedir, passphrase):
    command = [
        which('gpg2') or which('gpg'),
        '--batch',
        '--no-tty',
        '--always-trust',
        '--recipient', recipient,
        '--homedir', homedir,
        '--passphrase', passphrase,
        '--emit-version',
        '-o', '-',
        '-d', '-',
    ]
    response = run(command, data=data)
    return response.std_out


def setup_homedir(public_key, private_key):
    homedir = mkdtemp()
    keysfile = NamedTemporaryFile("w")
    with open(keysfile.name, "w") as f:
        f.write(public_key)
        f.write(private_key)
    import_keys(keysfile.name, homedir)
    return homedir


#############################
# database
#############################

def split_fullname(fullname):
    regex = re.compile(r'(?:(?P<login>.+?(?:\@.+?)?)@(?P<name>.+?$))')
    regex_name_only = re.compile(r'(?P<at>@)?(?P<name>.+?$)')

    if regex.match(fullname):
        mobj = regex.match(fullname)
    elif regex_name_only.match(fullname):
        mobj = regex_name_only.match(fullname)
    else:
        raise ValueError("Not a valid name")

    if mobj.groupdict().get('at'):
        login = ""
    else:
        login = mobj.groupdict().get('login')
    name = mobj.groupdict().get("name")

    return login, name


def make_fullname(login, name):
    fullname = "{}@{}".format("" if login is None else login, name)
    return fullname


class Database(TinyDB):

    def __init__(self, config, passphrase=None):
        self.passphrase = passphrase
        super(Database, self).__init__(
            safe_join(config["PATH"], "credentials.json"),
            default_table="credentials")
        self.config = config
        self._setup_keyring()
        self.repo = Repo(self.config["PATH"], autopush=self.config["AUTOPUSH"])

    def _setup_keyring(self):
        public_key = self.config["KEYS"]["PUBLIC"]
        private_key = self.config["KEYS"]["PRIVATE"]
        if public_key and private_key:
            homedir = setup_homedir(public_key, private_key)
            recipient = get_default_recipient(homedir)
            self.config["HOMEDIR"] = homedir
            self.config["RECIPIENT"] = recipient

    def ensure_passphrase(self):
        encrypted_dict = self.encrypt({"password": "OK"})
        decrypted_dict = self.decrypt(encrypted_dict)
        if decrypted_dict["password"] != "OK":
            raise ValueError("Wrong passphrase")

    def query(self, fullname):
        login, name = split_fullname(fullname)
        if login:
            return (Query().name == name) & (Query().login == login)
        else:
            return (Query().name == name)

    def encrypt(self, credential):
        credential = deepcopy(credential)
        credential["password"] = encrypt(
            credential["password"],
            self.config["RECIPIENT"] or get_default_recipient(),
            self.config["HOMEDIR"]
        )
        return credential

    def decrypt(self, credential):
        credential = deepcopy(credential)
        credential["password"] = decrypt(
            credential["password"],
            self.config["RECIPIENT"] or get_default_recipient(),
            self.config["HOMEDIR"],
            self.passphrase
        )
        return credential


#############################
# git
#############################
class Repo(object):

    def __init__(self, path, autopush=None):
        self.path = path
        self.autopush = parse_remote(autopush) if autopush else ["origin", "master"]

    def init(self):
        run(["git", "init"], cwd=self.path)
        return self

    def push(self):
        run(["git", "push"] + list(self.autopush), cwd=self.path)
        return self

    def commit(self, message):
        run(["git", "add", "."], cwd=self.path)
        run(["git", "commit", "-m", message], cwd=self.path)
        if self.autopush:
            self.push()
        return self


#############################
# cli
#############################

def pass_db(ensure_passphrase=False, confirm_passphrase=False):
    def decorator(func):
        def ensure_passphrase_wrapper(f):
            @functools.wraps(f)
            def new_func(db, *args, **kwargs):
                if ensure_passphrase:
                    passphrase = db.passphrase
                    if not passphrase:
                        passphrase = click.prompt(
                            "Passphrase",
                            hide_input=True,
                            confirmation_prompt=confirm_passphrase,
                        )
                    db.passphrase = passphrase
                    try:
                        db.ensure_passphrase()
                    except ValueError as e:
                        raise click.ClickException("{}".format(e))
                return f(db, *args, **kwargs)
            return new_func
        return click.make_pass_decorator(Database, ensure=True)(
            ensure_passphrase_wrapper(func))
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


def parse_remote(value):
    try:
        remote, branch = value.split('/')
        return [remote, branch]
    except ValueError:
        raise []


def prompt_update(credential, field, hidden=False):
    value = credential[field]
    prompt = "{} [{}]".format(field.title(), "*****" if hidden else value)
    return click.prompt(prompt,
                        hide_input=hidden,
                        confirmation_prompt=hidden,
                        default=value,
                        show_default=False)


@click.group()
@click.option("-D", "--database", help="Database path", envvar="PASSPIE_DATABASE")
@click.option("-P", "--passphrase", help="Database passphrase", envvar="PASSPIE_PASSPHRASE")
@click.option("-A", "--autopush", help="Autopush git [origin/master]", envvar="PASSPIE_AUTOPUSH")
@click.pass_context
def cli(ctx, database, passphrase, autopush):
    config_overrides = {}
    if database:
        config_overrides["PATH"] = database
    if autopush:
        config_overrides["AUTOPUSH"] = autopush
    config = config_load(config_overrides)

    if ctx.invoked_subcommand == "init":
        ctx.obj = {"config": config, "passphrase": passphrase}
    else:
        db = Database(config=config, passphrase=passphrase)
        ctx.obj = db


@cli.command()
@click.option("-f", "--force", is_flag=True, help="Force initialization")
@click.option("-r", "--recipient", help="Keyring recipient")
@click.pass_context
def init(ctx, force, recipient):
    """Initialize database"""
    config = ctx.obj["config"]
    passphrase = ctx.obj["passphrase"]
    if not passphrase:
        passphrase = click.prompt(
            "Passphrase",
            hide_input=True,
            confirmation_prompt=True,
        )

    db_path = config["PATH"]

    if os.path.isdir(db_path) and not force:
        msg = "Path '{}' exists [--force] to overwrite".format(db_path)
        raise click.ClickException(msg)
    elif os.path.isdir(db_path):
        shutil.rmtree(db_path)

    mkdir(db_path)
    db = Database(config)

    config_values = {}
    if recipient:
        config_values["recipient"] = recipient
    else:
        public_key, private_key = create_keys(passphrase)
        config_values["KEYS"] = {}
        config_values["KEYS"]["PUBLIC"] = public_key
        config_values["KEYS"]["PRIVATE"] = private_key

    with open(safe_join(db_path, ".config"), "w") as f:
        f.write(yaml_dump(config_values))

    db.repo.init().commit("Initialize database")


@cli.command(name="list")
@pass_db()
def listdb(db):
    """List credentials as table"""
    table = Table(db.config)
    click.echo(table.render(db.all()))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-c", "--comment", default="", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-f", "--force", is_flag=True, help="Force overwrite existing credential")
@pass_db()
def add(db, fullnames, random, comment, password, force):
    """Insert credential"""
    for fullname in fullnames:
        if random or db.config["RANDOM"]:
            password = genpass(db.config["PATTERN"])
        elif password is None:
            prompt = "Password for {}".format(password)
            password = click.prompt(prompt, hide_input=True,
                                    confirmation_prompt=True)
        login, name = split_fullname(fullname)
        credential = {
            "name": name,
            "login": login,
            "password": password,
            "comment": comment,
        }
        if db.contains(db.query(fullname)):
            if force or click.confirm("Overwrite {}".format(fullname)):
                db.update(credential, db.query(fullname))
        else:
            db.insert(db.encrypt(credential))
    else:
        db.repo.commit("Add credentials '{}'".format((", ").join(fullnames)))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-f", "--force", is_flag=True, help="Force removing credentials")
@pass_db()
def remove(db, fullnames, force):
    """Remove credential"""
    removed = False
    for fullname in [f for f in fullnames if db.contains(db.query(f))]:
        if force or click.confirm("Remove {}".format(fullname)):
            db.remove(db.query(fullname))
            removed = True

    if removed is True:
        db.repo.commit("Remove credentials '{}'".format((", ").join(fullnames)))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-P", "--pattern", help="Random password pattern")
@click.option("-C", "--copy", is_flag=True, help="Copy passwor to clipboard")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.option("-c", "--comment", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-l", "--login", help="Credentials login")
@click.option("-n", "--name", help="Credentials name")
@pass_db(ensure_passphrase=True)
def update(db, fullnames, random, pattern, copy, comment, password, name, login, yes):
    """Update credential"""
    updated = []
    for fullname in [f for f in fullnames if db.contains(db.query(f))]:
        if yes is True or click.confirm("Update {}".format(fullname)):
            cred = db.get(db.query(fullname))
            values = {}
            if login:
                values["login"] = login
            if name:
                values["name"] = name
            if password:
                values["password"] = password
            if comment:
                values["comment"] = comment
            if random:
                values["password"] = genpass(pattern or db.config["PATTERN"])

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
            copy_to_clipboard(cred["password"], db.config["COPY_TIMEOUT"])


@cli.command()
@click.argument("fullname")
@click.argument("dest", type=click.File("w"), required=False)
@click.option("-t", "--timeout", type=int, default=0, help="Timeout to clear clipboard")
@pass_db(ensure_passphrase=True)
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
@click.argument("filepath", type=click.Path(readable=True, exists=True))
@click.option("-I", "--importer", type=click.Choice(importers.get_names()),
              help="Specify an importer")
@click.option("--cols", help="CSV expected columns", callback=validate_cols)
@click.option("-f", "--force", is_flag=True, help="Force importing credentials")
@pass_db()
def import_database(db, filepath, importer, cols, force):
    """Import credentials from path"""
    if cols:
        importer = importers.get(name='csv')
        kwargs = {'cols': cols}
    else:
        importer = importers.find_importer(filepath)
        kwargs = {}

    imported = False
    if importer:
        credentials = [db.encrypt(c) for c in importer.handle(filepath, **kwargs)]
        for credential in credentials:
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
        db.repo.commit(message=u'Imported credentials from {}'.format(filepath))


@cli.command(name="export")
@click.argument("filepath", type=click.File("w"))
@click.option("--json", "as_json", is_flag=True, help="Export as JSON")
@pass_db(ensure_passphrase=True)
def export_database(db, filepath, as_json):
    """Export credentials in plain text"""
    credentials = (db.decrypt(c) for c in db.all())
    dict_content = OrderedDict()
    dict_content["handler"] = "passpie"
    dict_content["version"] = 1.0
    dict_content["credentials"] = [dict(x) for x in credentials]

    if as_json:
        content = json.dumps(dict_content, indent=2)
    else:
        dict_content = dict(dict_content)
        content = yaml.safe_dump(dict_content, default_flow_style=False)

    filepath.write(content)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@pass_db()
def git(db, command):
    """Git commands"""
    cmd = ["git"] + list(command)
    run(cmd, cwd=db.config["PATH"], pipe=False)
