# -*- coding: utf-8 -*-
from contextlib import contextmanager
from copy import deepcopy
from collections import namedtuple, OrderedDict
from subprocess import Popen, PIPE
from tempfile import mkdtemp, NamedTemporaryFile
import bz2
import errno
import functools
import gzip
import json
import logging
import os
import re
import shutil
import sys
import tarfile
import time
import zipfile


from tabulate import tabulate
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import click
import pyperclip
import rstr
import yaml

from . import importers
from ._compat import *


logger = logging.getLogger('passpie')
logger_handler = logging.StreamHandler()
logger_formatter = logging.Formatter("%(levelname)s:passpie.%(module)s:%(message)s")
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
logger.setLevel(logging.CRITICAL)


#############################
# process
#############################

DEVNULL = open(os.devnull, 'w')

Response = namedtuple("Response", "cmd std_out std_err returncode")


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

    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("run(command):%s", " ".join(cmd))
        if std_err and std_err.strip():
            logger.debug(std_err)
        if response.returncode != 0:
            logger.debug("run(command):error(%s):%s", response.returncode, response)
    return response


#############################
# utils
#############################

def safe_join(*paths):
    return os.path.join(*[os.path.expanduser(p) for p in paths])


def yaml_dump(data):
    return yaml.safe_dump(data, default_flow_style=False)


def yaml_to_python(data):
    return yaml.safe_load("[%s]" % data)[0]


def yaml_load(path, ensure=False):
    yaml_content = {}
    try:
        with open(path) as f:
            yaml_content = yaml.safe_load(f.read())
    except IOError:
        logger.info(u'YAML file "{}" not found'.format(path))
    except yaml.scanner.ScannerError as e:
        raise click.ClickException(u'Malformed YAML file: {}'.format(e))

    if not yaml_content and ensure is True:
        raise RuntimeError("YAML content is empty and ensure is True")
    else:
        return yaml_content


def genpass(pattern):
    """generates a password with random chararcters
    examples:
      cat /dev/urandom | strings

    """
    try:
        return rstr.xeger(pattern)
    except re.error as e:
        raise ValueError(str(e))


def which(*binaries):
    try:
        from shutil import which as _which
    except ImportError:
        from distutils.spawn import find_executable as _which

    for binary in binaries:
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

HOME = os.path.expanduser("~")
HOME_CONFIG_PATH = safe_join(HOME, ".passpierc")
DEFAULT_CONFIG = {
    # Database
    'DATABASE': "passpie.db",
    'GIT': True,
    'GIT_PUSH': None,

    # GPG
    'KEY_LENGTH': 4096,
    'HOMEDIR': None,
    'RECIPIENT': None,

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
    'PASSWORD_PATTERN': "[a-zA-Z0-9=+_*!?&%$# ]{32}",
    'PASSWORD_RANDOM': False,

    # Cli
    'VERBOSE': False,
    'DEBUG': False,
}


def config_create(path, values={}):
    with open(path, "w") as f:
        f.write(yaml_dump(values))


def config_default():
    cfg = deepcopy(DEFAULT_CONFIG)
    for k in cfg.keys():
        environ_name = "PASSPIE_{}".format(k.upper())
        environ_value = os.environ.get(environ_name)
        if environ_value:
            cfg[k] = yaml_to_python(environ_value)
    return cfg


def config_load(overrides):
    cfg = config_default()
    cfg.update(yaml_load(HOME_CONFIG_PATH))
    cfg.update(overrides)
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
Name-Comment: {}
Passphrase: {}
Name-Real: {}
Name-Email: {}
Expire-Date: {}
%commit
"""


def ensure_keys(path):
    keys_path = safe_join(os.path.expanduser(path), '.keys')
    if os.path.isfile(keys_path):
        return keys_path


def make_key_input(**kwargs):
    kwargs.setdefault("key_length", 4096)
    kwargs.setdefault("name", "Passpie")
    kwargs.setdefault("email", "passpie@localhost")
    kwargs.setdefault("comment", "Generated by Passpie")
    kwargs.setdefault("expire_date", 0)
    key_input = KEY_INPUT.format(
        kwargs["key_length"],
        kwargs["comment"] or "Generated by passpie",
        kwargs["passphrase"],
        kwargs["name"],
        kwargs["email"],
        kwargs["expire_date"],
    )
    return key_input


def import_keys(keys_path, homedir):
    command = [
        which('gpg2', 'gpg'),
        '--no-tty',
        '--batch',
        '--no-secmem-warning',
        '--no-permission-warning',
        '--allow-secret-key-import',
        '--no-mdc-warning',
        '--homedir', homedir,
        '--import', keys_path
    ]
    ret = run(command)
    return ret.std_out


def list_keys(homedir):
    command = [
        which("gpg2", "gpg"),
        '--no-tty',
        "--batch",
        '--fixed-list-mode',
        '--with-colons',
        "--homedir", homedir,
        "--list-keys",
        "--fingerprint",
    ]
    response = run(command)
    keys = []
    for line in response.std_out.splitlines():
        mobj = re.search(r'fpr:.*?(\w+):', line)
        if mobj:
            fingerprint = mobj.group(1)
            keys.append(fingerprint)
    return keys


def export_keys(homedir, fingerprint, private=False):
    command = [
        which('gpg2', 'gpg'),
        '--no-tty',
        '--batch',
        '--homedir', homedir,
        '--export-secret-keys' if private else '--export',
        '--armor',
        '-o', '-',
        fingerprint,
    ]
    ret = run(command)
    return ret.std_out


def create_keys(passphrase, key_length=4096):
    homedir = mkdtemp()
    command = [
        which('gpg2', 'gpg'),
        '--batch',
        '--no-tty',
        '--homedir', homedir,
        '--gen-key',
    ]
    key_input = make_key_input(passphrase=passphrase, key_length=key_length)
    run(command, data=key_input)
    return homedir


def generate_key(homedir, values):
    command = [
        which('gpg2', 'gpg'),
        '--batch',
        '--no-tty',
        '--homedir', homedir,
        '--gen-key',
    ]
    key_input = make_key_input(**values)
    run(command, data=key_input)


def get_default_recipient(homedir):
    recipient = next((k for k in list_keys(homedir)), None)
    if recipient is None:
        info = "default recipient not found at homedir: {}".format(homedir)
        logger.debug(info)
    return recipient


def encrypt(data, recipient, homedir):
    command = [
        which('gpg2', 'gpg'),
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
        which('gpg2', 'gpg'),
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
        raise ValueError("not a valid fullname: {}".format(fullname))

    match_dict = mobj.groupdict()
    login = match_dict.get('login', "")
    name = match_dict.get("name")

    return login, name


def make_fullname(login, name):
    fullname = "{}@{}".format("" if login is None else login, name)
    return fullname


def find_database_root(path):
    for root, dirs, files in os.walk(path):
        if "credentials.json" or ".passpie" in files:
            return root


def archive(src, dest, format):
    if format == "dir":
        tpath = src
    else:
        tfile = NamedTemporaryFile()
        tpath = shutil.make_archive(tfile.name, format, src)
    shutil.move(tpath, dest)


def find_compression_type(filename):
    with gzip.GzipFile(filename) as gzfile:
        try:
            gzfile.read()
            return "gz"
        except IOError:
            pass

    with bz2.BZ2File(filename) as bzfile:
        try:
            bzfile.read()
            return "bz2"
        except IOError:
            pass


def is_git_url(path):
    regex = re.compile(
        r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?'
    )
    if path and regex.match(path):
        return True
    else:
        return False


def find_source_format(path):
    try:
        if is_git_url(path):
            return "git"
        elif os.path.isdir(path):
            return "dir"
        elif tarfile.is_tarfile(path):
            compression = find_compression_type(path)
            if compression == "gz":
                return "gztar"
            elif compression == "bz2":
                return "bztar"
            else:
                return "tar"
        elif zipfile.is_zipfile(path):
            return "zip"
    except (IOError, TypeError):
        logger.info("unrecognized source path: ".format(path))
        return None


def has_required_database_files(path):
    return all(f in os.listdir(path) for f in Database.REQUIRED_FILES)


def setup_path(path):
    source_format = find_source_format(path)

    if source_format is None:
        return None
    elif source_format == "dir":
        dir_path = path
    elif source_format == "git":
        dir_path = clone(path)
    elif source_format in ("tar", "gztar", "bztar"):
        dir_path = mkdtemp()
        with tarfile.open(path) as tf:
            tf.extractall(dir_path)
    elif source_format == "zip":
        dir_path = mkdtemp()
        with zipfile.open(path) as zf:
            zf.extractall(dir_path)
    else:
        raise RuntimeError("Unrecognized database format: {}".format(path))

    # Find database root
    dir_path = find_database_root(dir_path)
    if dir_path is not None and has_required_database_files(dir_path):
        return dir_path
    else:
        raise RuntimeError("Database is missing required files: {}".format(path))


def import_keyring(keyring):
    homedir = mkdtemp()
    for keys in keyring:
        keysfile = NamedTemporaryFile("w")
        with open(keysfile.name, "w") as f:
            f.write(keys)
        import_keys(keysfile.name, homedir)
    return homedir


def setup_homedir(path):
    if os.path.exists(path):
        keyring = yaml_load(safe_join(path, "keys.yml"))
        if keyring:
            return import_keyring(keyring)
    else:
        raise ValueError("couldn't create homedir ")


def setup_config(path, default=None):
    if path and os.path.exists(path):
        config = deepcopy(default)
        config.update(yaml_load(safe_join(path, "config.yml")))
        return config
    return default


class Database(TinyDB):
    REQUIRED_FILES = (".passpie",)

    def __init__(self, config, passphrase=None):
        self.passphrase = passphrase
        self.src = config["DATABASE"]
        self.path = setup_path(self.src)
        self.config = setup_config(self.path, config)
        self.repo = Repo(self.path)
        self.homedir = self.config["HOMEDIR"] or setup_homedir(self.path)
        self.recipient = (
            self.config["RECIPIENT"] or
            get_default_recipient(self.homedir) if self.homedir else None)
        if self.path:
            dbfile_path = safe_join(self.path, "credentials.json")
            super(Database, self).__init__(dbfile_path, default_table="credentials")
        else:
            super(Database, self).__init__(default_table="credentials", storage=MemoryStorage)

    @property
    def config_path(self):
        return safe_join(self.path, "keys.yml")

    def archive(self):
        # Write keys.yml
        fingerprints = list_keys(self.homedir)
        keys = []
        for fingerprint in fingerprints:
            pubkey = export_keys(self.homedir, fingerprint, private=False)
            seckey = export_keys(self.homedir, fingerprint, private=True)
            keys.append(pubkey + seckey)
        with open(self.config_path, "w") as f:
            f.write(yaml_dump(keys))

        # Write config.yml
        pass

        # Generate archive if needed
        format = find_source_format(self.src)
        if format in ("gztar", "zip", "bztar", "tar"):
            archive(src=self.path, dest=self.src, format=format)

    def config_set(self, name, value):
        self.config[name] = value
        with open(safe_join(self.path, "config.yml"), "w") as f:
            cfg = {k: v for k, v in self.config.items()
                   if config_default()[k] != self.config[k]}
            f.write(yaml_dump(cfg))

    def ensure_passphrase(self):
        if self.passphrase is None:
            raise ValueError("Passphrase not set")
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
            self.recipient,
            self.homedir
        )
        return credential

    def decrypt(self, credential):
        credential = deepcopy(credential)
        credential["password"] = decrypt(
            credential["password"],
            self.recipient,
            self.homedir,
            self.passphrase
        )
        return credential


#############################
# git
#############################
def ensure_git(repository_exists=True):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            if not which("git"):
                logger.info("git not found. -- mocking call --")
            elif (repository_exists is True and
                  not os.path.exists(safe_join(self.path, ".git"))):
                logger.info("git repository not found. -- mocking call --")
            else:
                return f(self, *args, **kwargs)
            return self
        return wrapper
    return decorator


class Repo(object):

    def __init__(self, path):
        self.path = path

    @ensure_git(repository_exists=False)
    def init(self):
        run(["git", "init"], cwd=self.path)
        return self

    @ensure_git()
    def push(self, remote="origin", branch="master"):
        run(["git", "push", remote, branch], cwd=self.path)
        return self

    @ensure_git()
    def commit(self, message):
        run(["git", "add", "."], cwd=self.path)
        run(["git", "commit", "-m", message], cwd=self.path)
        return self


def parse_remote(arg):
    origin, branch = arg.split("/")
    return origin, branch


def clone(url, dest=None, depth=None):
    if dest and os.path.exists(dest):
        raise FileExistsError('Destination already exists: %s' % dest)
    dest = dest if dest else mkdtemp()
    cmd = ['git', 'clone', url, dest]
    if depth:
        cmd += ['--depth', depth]
    run(cmd)
    return dest


#############################
# cli
#############################

def close_database(db, sync):
    logger.info("[closing database]")
    if sync:
        logger.info("[closing database]:archiving to %s" % db.src)
        db.archive()
        if db.config["GIT_PUSH"]:
            remote, branch = parse_remote(db.config["GIT_PUSH"])
            logger.info("[closing database]:pushing to git remote")
            db.repo.push(remote, branch)


def pass_db(ensure_passphrase=False, confirm_passphrase=False, ensure_exists=True, sync=True):
    def decorator(func):
        def ensure_passphrase_wrapper(f):
            @functools.wraps(func)
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
                if ensure_exists and db.path is None:
                    raise click.ClickException(
                        "Database not found at path: {}".format(db.src))
                result = f(db, *args, **kwargs)
                close_database(db, sync)
                return result
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


def validate_yaml_str(ctx, param, value):
    if value:
        try:
            return yaml_to_python(value)
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
@click.option("-D", "--database", help="Database path")
@click.option("-P", "--passphrase", help="Database passphrase")
@click.option("-g", "--git-push", help="Autopush git [origin/master]")
@click.option('--verbose', is_flag=True, help='Activate verbose output')
@click.option('--debug', is_flag=True, help='Activate debug output')
@click.pass_context
def cli(ctx, database, passphrase, git_push, verbose, debug):
    config_overrides = {}
    if database:
        config_overrides["DATABASE"] = database
    if git_push:
        config_overrides["GIT_PUSH"] = git_push

    config = config_load(config_overrides)

    if verbose is True or config["VERBOSE"] is True:
        logger.setLevel(logging.INFO)
    if debug is True or config["DEBUG"] is True:
        logger.setLevel(logging.DEBUG)

    if ctx.invoked_subcommand == "init":
        ctx.meta["config"] = config
        ctx.meta["passphrase"] = passphrase
    else:
        db = Database(config=config, passphrase=passphrase)
        ctx.obj = db


@cli.command()
@click.argument("path", default="passpie.db")
@click.option("-f", "--force", is_flag=True, help="Force initialization")
@click.option("-r", "--recipient", help="Keyring recipient")
@click.option("-ng", "--no-git", is_flag=True, help="Don't initialize a git repo")
@click.option("-F", "--format", default="gztar", type=click.Choice(["dir", "tar", "zip", "gztar", "bztar"]))
@click.pass_context
def init(ctx, path, force, recipient, no_git, format):
    """Initialize database"""
    config = ctx.meta["config"]
    passphrase = ctx.meta["passphrase"]
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

    tempdir = mkdtemp()
    config_values = {}
    keys = []
    if recipient:
        config_values["RECIPIENT"] = recipient
    else:
        homedir = create_keys(passphrase=passphrase, key_length=config["KEY_LENGTH"])
        recipient = get_default_recipient(homedir)
        pubkey = export_keys(homedir, recipient, private=False)
        seckey = export_keys(homedir, recipient, private=True)
        keys = [pubkey + seckey]

    # Create files: keys.yml, config.yml, .passpie
    with open(safe_join(tempdir, "keys.yml"), "w") as f:
        f.write(yaml_dump(keys))
    with open(safe_join(tempdir, "config.yml"), "w") as f:
        f.write(yaml_dump(config_values))
    with open(safe_join(tempdir, ".passpie"), "w"):
        pass

    if no_git or config["GIT"] is False:
        # Don't create a git repo
        pass
    else:
        repo = Repo(tempdir)
        repo.init().commit("Initialize database")
    archive(src=tempdir, dest=path, format=format)


@cli.command(name="list")
@pass_db(sync=False)
@click.argument("grep", required=False)
def listdb(db, grep):
    """List credentials as table"""
    if grep:
        query = (Query().login.search(".*{}.*".format(grep)) |
                 Query().name.search(".*{}.*".format(grep)) |
                 Query().comment.search(".*{}.*".format(grep)))
        credentials = db.search(query)
    else:
        credentials = db.all()

    if credentials:
        table = Table(db.config)
        click.echo(table.render(credentials))


@cli.command(name="config")
@click.argument("name", required=False, type=str)
@click.argument("value", required=False, type=str, callback=validate_yaml_str)
@pass_db(sync=False)
def configdb(db, name, value):
    """Configuration settings"""
    name = name.upper() if name else ""
    if name and name in db.config:
        if value:
            db.config_set(name, value)
            db.repo.commit("Set config: {} = {}".format(name, value))
            close_database(db, sync=True)
        else:
            click.echo("{}: {}".format(name, db.config[name]))
    else:
        click.echo(yaml_dump(db.config).strip())


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-c", "--comment", default="", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-f", "--force", is_flag=True, help="Force overwrite existing credential")
@pass_db()
def add(db, fullnames, random, comment, password, force):
    """Insert credential"""
    if random or db.config["PASSWORD_RANDOM"]:
        password = genpass(db.config["PASSWORD_PATTERN"])
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
                db.update(db.encrypt(credential), db.query(fullname))
            else:
                msg = "Credential {} exists. `--force` to overwrite".format(fullname)
                raise click.ClickException(msg)
        else:
            db.insert(db.encrypt(credential))
    else:
        db.repo.commit("Add credentials '{}'".format((", ").join(fullnames)))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.option("-A", "--all", "purge", is_flag=True, help="Purge all credentials")
@pass_db()
def remove(db, fullnames, yes, purge):
    """Remove credential"""
    if purge:
        db.purge()
        db.repo.commit("Purge credentials")
    else:
        removed = False
        fulnames = [f for f in fullnames if db.contains(db.query(f))]
        for fullname in fulnames:
            if yes or click.confirm("Remove {}".format(fullname)):
                db.remove(db.query(fullname))
                removed = True
        if removed is True:
            msg = "Remove credentials '{}'".format((", ").join(fullnames))
            db.repo.commit(msg)


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
@pass_db(ensure_passphrase=True, sync=False)
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
    run(cmd, cwd=db.path, pipe=False)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@click.option("--gen-key", is_flag=True, help="Generate keys")
@pass_db()
def gpg(db, command, gen_key):
    """GPG commands"""
    if gen_key:
        values = {
            "key_length": click.prompt("Key length", default=4096),
            "name": click.prompt("Name"),
            "email": click.prompt("Email"),
            "comment": click.prompt("Comment", default=""),
            "passphrase": click.prompt("Passphrase", hide_input=True, confirmation_prompt=True),
            "expire_date": click.prompt("Expire date", default=0),
        }
        homedir = db.homedir
        generate_key(homedir, values)
    else:
        cmd = [which("gpg2", "gpg"), "--homedir", db.homedir] + list(command)
        run(cmd, cwd=db.path, pipe=False)
