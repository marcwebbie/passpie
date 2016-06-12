# -*- coding: utf-8 -*-
from copy import deepcopy
import functools
import os
import re
import sys
import time

from tabulate import tabulate
from tinydb import TinyDB, Query
import click
import pyperclip
import rstr
import yaml


#############################
# utils
#############################

def safe_join(*paths):
    return os.path.join(*[os.path.expanduser(p) for p in paths])


def genpass(pattern):
    """generates a password with random chararcters
    examples:
      cat /dev/urandom | strings

    """
    try:
        return rstr.xeger(pattern)
    except re.error as e:
        raise ValueError(str(e))


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


#############################
# configuration
#############################

HOMEDIR = os.path.expanduser("~")
HOMEDIR_CONFIG_PATH = safe_join(HOMEDIR, ".passpieconfig")
DEFAULT_CONFIG = {
    # Database
    'PATH': safe_join(HOMEDIR, ".passpie"),
    'GIT': True,
    'AUTOPUSH': 'origin/master',
    'ENCRYPTED_FIELDS': ['password'],

    # GPG
    'KEY_LENGTH': 4096,
    'PASSPHRASE': None,
    'HOMEDIR': os.path.join(os.path.expanduser('~/.gnupg')),
    'RECIPIENT': None,

    # Table
    'TABLE_FORMAT': 'simple',
    'TABLE_SHOW_PASSWORD': True,  # False,
    'TABLE_HIDDEN_STRING': u'********',
    'TABLE_FIELDS': ['name', 'login', 'password', 'comment'],
    'TABLE_STYLE': {'login': {"fg": 'green'}, 'name': {"fg": 'yellow'}},

    # Credentials
    'COPY_TIMEOUT': 0,
    'PATTERN': "[a-zA-Z0-9=+_*!?&%$# ]{32}",
    'RANDOM': True,
}


def config_from_file(path):
    cfg = {}
    if os.path.exists(path):
        cfg = yaml.safe_load(path)
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

    def __init__(self, config_overrides):
        self.config = self._load_config(config_overrides)
        super(Database, self).__init__(safe_join(self.config["PATH"], "credentials.json"))

    def _load_config(self, config_overrides):
        cfg = deepcopy(DEFAULT_CONFIG)
        cfg.update(config_from_file(safe_join(HOMEDIR, ".passpieconfig")))
        cfg.update(config_overrides)
        cfg.update(config_from_file(safe_join(cfg["PATH"], ".passpieconfig")))
        return cfg

    def query(self, fullname):
        login, name = split_fullname(fullname)
        if login:
            return (Query().name == name) & (Query().login == login)
        else:
            return (Query().name == name)


#############################
# cli
#############################

def pass_db(ensure_passphrase=False):
    def decorator(func):
        def ensure_passphrase_wrapper(f):
            @functools.wraps(f)
            def new_func(db, *args, **kwargs):
                if db.config["PASSPHRASE"] is None and ensure_passphrase:
                    passphrase = click.prompt(
                        "Passphrase",
                        hide_input=True,
                    )
                    db.config["PASSPHRASE"] = passphrase
                return f(db, *args, **kwargs)
            return new_func
        return click.make_pass_decorator(Database, ensure=True)(
            ensure_passphrase_wrapper(func))
    return decorator


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    config_overrides = {}
    db = Database(config_overrides)
    ctx.obj = db


@cli.command(name="list")
@pass_db()
def listdb(db):
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
            db.insert(credential)


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-f", "--force", is_flag=True, help="Force removing credentials")
@pass_db()
def rm(db, fullnames, force):
    for fullname in [f for f in fullnames if db.contains(db.query(f))]:
        if force or click.confirm("Update {}".format(fullname)):
            db.remove(db.query(fullname))


@cli.command()
@click.argument("fullnames", nargs=-1, callback=lambda ctx, param, val: list(val))
@click.option("-r", "--random", is_flag=True, help="Random password generation")
@click.option("-f", "--force", is_flag=True, help="Force updating credentials")
@click.option("-c", "--comment", help="Credentials comment")
@click.option("-p", "--password", help="Credentials password")
@click.option("-l", "--login", help="Credentials login")
@click.option("-n", "--name", help="Credentials name")
@pass_db(ensure_passphrase=True)
def update(db, fullnames, random, comment, password, name, login, force):
    def prompt_update(credential, field, hidden=False):
        fullname = make_fullname(credential["login"], credential["name"])
        value = credential[field]
        prompt = "{} {} [{}]".format(
            field.title(), fullname, "*****" if hidden else value
        )
        return click.prompt(prompt,
                            hide_input=hidden,
                            confirmation_prompt=hidden,
                            default=value,
                            show_default=False)

    for fullname in [f for f in fullnames if db.contains(db.query(f))]:
        if force is False and not click.confirm("Update {}".format(fullname)):
            continue

        cred = db.get(db.query(fullname))
        login = login if login is not None else prompt_update(cred, "login")
        name = name if name is not None else prompt_update(cred, "name")
        password = password if password is not None else prompt_update(cred, "password", hidden=True)
        comment = comment if comment is not None else prompt_update(cred, "comment")

        values = {
            "login": login,
            "name": name,
            "password": password,
            "comment": comment,
        }
        db.update(values, db.query(fullname))


@cli.command()
@click.argument("fullname")
@click.argument("dest", type=click.File("w"), required=False)
@click.option("-t", "--timeout", type=int, default=0, help="Timeout to clear clipboard")
@pass_db(ensure_passphrase=True)
def copy(db, fullname, dest, timeout):
    credential = db.get(db.query(fullname))
    if credential:
        password = credential["password"]
        if dest:
            dest.write(password)
        else:
            copy_to_clipboard(password, timeout)
