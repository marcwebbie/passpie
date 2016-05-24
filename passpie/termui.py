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


def ensure_passphrase(passphrase, gpg, cfg):
    encrypted = gpg.encrypt('OK')
    decrypted = gpg.decrypt(encrypted, passphrase=passphrase)
    if not decrypted == 'OK':
        message = "Wrong passphrase"
        message_full = u"Wrong passphrase for recipient: {} in homedir: {}".format(
            cfg['recipient'],
            cfg['homedir'],
        )
        logging.error(message_full)
        raise click.ClickException(click.style(message, fg='red'))


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
