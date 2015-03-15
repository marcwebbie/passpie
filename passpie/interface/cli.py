from argparse import Namespace
from datetime import datetime
import os
import shutil

import click
from tinydb.queries import where

from passpie.crypt import Cryptor
from passpie.credential import split_fullname
from passpie.database import Database
from passpie.utils import genpass
from passpie._compat import FileExistsError

__version__ = "0.1.rc1"

config = Namespace(
    path=os.path.expanduser("~/.passpie"),
    show_password=False,
)


@click.group(invoke_without_command=True)
@click.option('-D', '--database', metavar="PATH", help="alternative database")
@click.option('-P', '--show-password', is_flag=True, help="show passwords")
@click.option('-v', '--verbose', is_flag=True, help="verbose debug output")
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, database, show_password, verbose):
    if ctx.invoked_subcommand is None:
        db = Database(config.path)
        for cred in sorted(db.all(), key=lambda x: x["login"]+x["name"]):
            click.echo("%(login)s@%(name)s" % cred)


@cli.command()
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


@cli.command()
@click.argument("fullname")
@click.password_option(help="credential password")
@click.option('-R', '--random', 'password', flag_value=genpass())
@click.option('-C', '--comment', default="", help="credential comment")
def add(fullname, password, comment):
    db = Database(config.path)
    login, name = split_fullname(fullname)

    found = db.get((where("login") == login) & (where("name") == name))
    if not found:
        with Cryptor(config.path) as cryptor:
            password = cryptor.encrypt(password)
        cred = dict(name=name,
                    login=login,
                    password=password,
                    comment=comment,
                    modified=datetime.now())
        db.insert(cred)
    else:
        click.echo("Credential {} already exists.".format(fullname))
        raise click.Abort


# @cli.command()
# @click.argument("fullname")
# @click.option("-R", "--random", help="generate random password",
#               flag_value=utils.genpass(__config__["random_length"]))
# @click.option('--password', metavar="PASSWORD", help="password")
# @click.option("--comment", default="", help="credential comment")
# def add(fullname, random, password, comment):
#     backend = Backend(__config__["database_path"], doctype=Credential)
#     if random:
#         password = random
#     elif not password:
#         password = click.prompt("Password", hide_input=True,
#                                 confirmation_prompt=True)
#     login, name = split_fullname(fullname)
#     values = {"name": name,
#               "login": login,
#               "password": crypt.encrypt(backend.path, password),
#               "comment": comment}
#     credential = Credential(values)
#     backend.insert(credential)


# @cli.command("print")
# def printdb():
#     database = Backend(__config__["database_path"], doctype=Credential)
#     headers = ["name", "login", "password", "comment"]
#     table = []
#     for credential in database.read():
#         row = [
#             click.style(credential.name, fg="yellow"),
#             credential.login,
#             "***",
#             credential.comment
#         ]
#         table.append(row)
#     click.echo(tabulate(table, headers))


# @cli.command()
# @click.argument("fullname")
# @click.option("-y", "--yes", is_flag=True, help="skip confimation prompts")
# def remove(fullname, yes):
#     database = Backend(__config__["database_path"], doctype=Credential)
#     matcher = Matcher(fullname=fullname)
#     matched_credentials = database.read(matcher)
#     if matched_credentials:
#         for c in matched_credentials:
#             click.echo(c)
#         if not yes:
#             yes = click.confirm(click.style("Remove", fg="red"))
#         if yes:
#             database.delete(matcher)


# @cli.command()
# @click.argument("fullname")
# @click.option("-s", "--search", is_flag=True,
# help="search by regex matching")
# @click.option("-y", "--yes", is_flag=True,
# help="skip confirmation prompt")
# @click.option("-R", "--random", is_flag=True,
# help="generate random password")
# def update(fullname, search, yes, random):
#     database = Backend(__config__["database_path"], doctype=Credential)
#     matcher = Matcher(fullname=fullname)
#     matched_credentials = database.read(matcher)
#     if matched_credentials:
#         for c in matched_credentials:
#             click.echo(c)

#         if not yes:
#             yes = click.confirm(click.style("Update", fg="red"))
#         if yes:
#             if random:
#                 password_default = utils.genpass(__config__.random_length)
#             else:
#                 password_default = "*****"

#             cred = matched_credentials[0]
#             name = click.prompt("Name", default=cred.name)
#             login = click.prompt("Login", default=cred.login)
#             password = click.prompt("Password", default=password_default,
#                                     confirmation_prompt=True,
# hide_input=True)
#             comment = click.prompt("Comment", default=cred.comment)

#             values = {"name": name, "login": login,
#                       "password": password, "comment": comment}
#             clean_values = {k: v for k, v in values.items()
#                             if values[k] != v or v != "*****"}

#             database.update(matcher, clean_values)


# @cli.command()
# @click.argument("fullname")
# @click.option("-s", "--search", is_flag=True,
# help="search by regex matching")
# @click.option('--passphrase', prompt=True, hide_input=True)
# def clipboard(fullname, search, passphrase):
#     database = Backend(__config__["database_path"], doctype=Credential)
#     matcher = Matcher(fullname=fullname)
#     matched_credentials = database.read(matcher)
#     if matched_credentials:
#         credential = matched_credentials[0]
#         pyperclip.copy(
#             crypt.decrypt(database.path, credential.password, passphrase))
#         click.echo("Copied '{}' password to clipboard".format(fullname))
