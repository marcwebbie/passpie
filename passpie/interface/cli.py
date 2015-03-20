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


def credential_confirmation_option(*param_decls, **attrs):
    def decorator(f):
        prompt = attrs.pop("prompt")

        def callback(ctx, param, value):
            if not value:
                prompt_text = "{} '{}'".format(
                    prompt, ctx.params["credential"]["fullname"])
                click.confirm(prompt_text, abort=True)

        attrs.setdefault('is_flag', True)
        attrs.setdefault('callback', callback)
        attrs.setdefault('expose_value', False)
        attrs.setdefault('help', 'Confirm the action without prompting.')
        return click.option(*(param_decls or ('--yes',)), **attrs)(f)
    return decorator


def passphrase_option(*param_decls, **attrs):
    def decorator(f):
        def callback(ctx, param, value):
            passphrase = value
            try:
                with Cryptor(config.path) as cryptor:
                    cryptor.check(passphrase, ensure=True)
                return passphrase
            except ValueError:
                click.secho("Wrong passphrase", fg="red")
                raise click.Abort

        attrs.setdefault('callback', callback)
        attrs.setdefault('prompt', True)
        attrs.setdefault('hide_input', True)
        return click.option(*(param_decls or ('--passphrase',)), **attrs)(f)
    return decorator


def credential_argument(*param_decls, **attrs):
    def decorator(f):
        def callback(ctx, param, value):
            fullname = value
            db = Database(config.path)
            credential = db.get(where("fullname") == fullname)
            if credential:
                return credential
            else:
                click.secho(
                    "Credential '{}' not found".format(fullname), fg="red")
            raise click.Abort

        attrs.setdefault('metavar', 'fullname')
        attrs.setdefault('callback', callback)
        attrs.setdefault("is_eager", True)
        return click.argument("credential", **attrs)(f)
    return decorator


@click.group(invoke_without_command=True)
@click.option('-D', '--database', metavar="PATH", help="alternative database")
@click.option('-v', '--verbose', is_flag=True, help="verbose debug output")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, verbose):
    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        credentials = sorted(db.all(), key=lambda x: x["name"]+x["login"])

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
@credential_argument()
@passphrase_option()
def copy(credential, passphrase):
    with Cryptor(config.path) as cryptor:
        decrypted = cryptor.decrypt(credential["password"], passphrase)
        pyperclip.copy(decrypted)
        click.echo("Password copied to clipboard".format(
            credential["fullname"]))


@cli.command(help="Update matched credentials")
@credential_argument()
@credential_confirmation_option(prompt="Update credential")
@click.option("--name", help="Credential new name")
@click.option("--login", help="Credential new login")
@click.option("--comment", help="Credential new comment")
@click.option("--password", help="Credential new password")
@click.option('--random', 'password', flag_value=genpass(),
              help="Credential new randomly generated password")
def update(credential, name, login, password, comment):
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
        values["fullname"] = make_fullname(values["login"], values["name"])
        values["modified"] = datetime.now()
        if values["password"] != credential["password"]:
            with Cryptor(config.path) as cryptor:
                values["password"] = cryptor.encrypt(password)
        db = Database(config.path)
        db.update(values, (where("fullname") == credential["fullname"]))
