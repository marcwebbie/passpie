from functools import wraps
import click

import logging


class AliasGroup(click.Group):

    def get_command(self, ctx, name):
        if name in getattr(ctx, 'config', {}).get('aliases', []):
            name = ctx.config['aliases'][name]
        cmd = super(AliasGroup, self).get_command(ctx, name)
        return cmd


def pass_context_object(attr_name, dest_name=None):
    def decorator(f):
        @click.pass_context
        @wraps(f)
        def new_func(ctx, *args, **kwargs):
            while True:
                obj = getattr(ctx, attr_name, None)
                if obj is not None:
                    if dest_name:
                        kwargs[dest_name] = obj
                        return ctx.invoke(f, *args, **kwargs)
                    return ctx.invoke(f, obj, *args, **kwargs)
                else:
                    ctx = ctx.parent
        return new_func
    return decorator


def password_prompt(text="Password", default=""):
    while True:
        while True:
            value = click.prompt(text, hide_input=True, default=default, show_default=False)
            if value or default is not None:
                break
        while 1:
            suffix = " [empty password]: " if value == "" else ": "
            value2 = click.prompt('Repeat for confirmation',
                                  hide_input=True,
                                  default=default,
                                  show_default=False,
                                  prompt_suffix=suffix)
            if value == value2:
                return value
        click.echo('Error: the two entered values do not match', err=False)


def ensure_passphrase(gpg, cfg, abort=True):
    encrypted = gpg.encrypt('OK')
    decrypted = gpg.decrypt(encrypted)
    if not decrypted == 'OK':
        message = "Wrong passphrase"
        message_full = u"Wrong passphrase for recipient: {} in homedir: {}".format(
            cfg['recipient'],
            cfg['homedir'],
        )
        logging.error(message_full)
        if abort is True:
            raise click.ClickException(click.style(message, fg='red'))
    return decrypted


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


def passphrase_required(ctx):
    protected_commands = ("copy", "reset", "export", "status", "init")
    cmd = ctx.invoked_subcommand
    if (ctx.config["private"] is True) or (cmd and (cmd in protected_commands)):
        return True
    else:
        return False


def passphrase_confirm_required(ctx):
    protected_commands = ("init")
    cmd = ctx.invoked_subcommand
    if cmd and (cmd in protected_commands):
        return True
    else:
        return False
