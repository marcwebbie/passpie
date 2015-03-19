from argparse import Namespace
from collections import OrderedDict
from datetime import datetime
from functools import partial
import os
import shutil

import click
import pyperclip
from tabulate import tabulate
from tinydb.queries import where

from passpie.crypt import Cryptor
from passpie.credential import split_fullname, make_fullname
from passpie.database import Database
from passpie.utils import genpass
from passpie._compat import FileExistsError

__version__ = "0.1.rc1"

config = Namespace(
    path=os.path.expanduser("~/.passpie"),
    show_password=False,
    headers=("name", "login", "password", "comment"),
    hidden=("password",),
    colors={"name": "yellow", "login": "green"},
    tablefmt="rst",
    missingval="*****"
)

tabulate = partial(tabulate,
                   headers="keys",
                   tablefmt=config.tablefmt,
                   numalign='left',
                   missingval=config.missingval)


@click.group(invoke_without_command=True)
@click.option('-D', '--database', metavar="PATH", help="alternative database")
@click.option('-v', '--verbose', is_flag=True, help="verbose debug output")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, verbose):
    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        credentials = sorted(db.all(), key=lambda x: x["login"]+x["name"])

        if credentials:
            table = OrderedDict()

            for header in config.headers:
                if header in config.hidden:
                    table[header] = [None for c in credentials]
                elif header in config.colors:
                    color = config.colors[header]
                    table[header] = [click.style(c.get(header, ""), color)
                                     for c in credentials]
                else:
                    table[header] = [c.get(header, "") for c in credentials]

            click.echo(tabulate(table))


@cli.command(help="Initialize new passpie database")
@click.option('--passphrase', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--force', is_flag=True, help="force overwrite database")
def init(passphrase, force):
    if force:
        shutil.rmtree(config.path)

    try:
        with Cryptor(config.path) as cryptor:
            cryptor.create_keys(passphrase)
    except FileExistsError:
        msg = "Database exists in {}. `--force` to overwrite"
        click.secho(msg.format(config.path), fg="yellow")
        raise click.Abort
    click.echo("Initialized database in {}".format(config.path))


@cli.command(help="Add new credential")
@click.argument("fullname")
@click.password_option(help="Credential password")
@click.option('-R', '--random', 'password', flag_value=genpass())
@click.option('-C', '--comment', default="", help="Credential comment")
def add(fullname, password, comment):
    db = Database(config.path)
    login, name = split_fullname(fullname)

    found = db.get((where("login") == login) & (where("name") == name))
    if not found:
        with Cryptor(config.path) as cryptor:
            password = cryptor.encrypt(password)

        cred = dict(fullname=fullname,
                    name=name,
                    login=login,
                    password=password,
                    comment=comment,
                    modified=datetime.now())
        db.insert(cred)
    else:
        click.echo("Credential {} already exists.".format(fullname))
        raise click.Abort


@cli.command(help="Copy credential password to clipboard")
@click.argument("fullname")
@click.option('--passphrase', prompt=True, hide_input=True,
              confirmation_prompt=True)
def copy(fullname, passphrase):
    db = Database(config.path)
    login, name = split_fullname(fullname)
    found = db.get((where("login") == login) & (where("name") == name))

    if not found:
        click.secho("Credential '{}' not found".format(fullname), fg="red")
        raise click.Abort
    else:
        with Cryptor(config.path) as cryptor:
            pyperclip.copy(cryptor.decrypt(found["password"], passphrase))
        click.echo("Password copied to clipboard".format(fullname))


@cli.command(help="Update matched credentials")
@click.argument("fullname")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.password_option(help="Credential new password")
@click.option('--random', 'password', flag_value=genpass(),
              help="Credential new randomly generated password")
@click.option("--comment", help="Credential new comment")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def update(fullname, name, login, password, comment, yes):
    db = Database(config.path)
    found = db.get(where("fullname") == fullname)

    if not found:
        click.echo("Credential '{}' not found".format(fullname))
        raise click.Abort
    else:
        if not yes:
            click.confirm("Update credential '{}'".format(fullname),
                          abort=True)

        values = {}
        if any([name, login, password, comment]):
            values["name"] = name if name else found["name"]
            values["login"] = login if login else found["login"]
            values["password"] = password if password else found["password"]
            values["comment"] = comment if comment else found["comment"]
            if password:
                with Cryptor(config.path) as cryptor:
                    values["password"] = cryptor.encrypt(password)
        else:
            values["name"] = click.prompt("Name", default=found["name"])
            values["login"] = click.prompt("Login", default=found["login"])
            values["password"] = click.prompt("Password", default="*****",
                                              confirmation_prompt=True,
                                              hide_input=True)
            values["comment"] = click.prompt("Comment",
                                             default=found["comment"])
            if values["password"] == "*****":
                values["password"] = found["password"]
            else:
                with Cryptor(config.path) as cryptor:
                    values["password"] = cryptor.encrypt(password)

        values["fullname"] = make_fullname(values["login"], values["name"])
        values["modified"] = datetime.now()

        db.update(values, (where("fullname") == fullname))
