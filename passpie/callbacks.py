import click

from .history import clone
from . import config


def validate_remote(ctx, param, value):
    if value:
        try:
            remote, branch = value.split('/')
            return (remote, branch)
        except ValueError:
            raise click.BadParameter('remote need to be in format <remote>/<branch>')


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


def load_config(ctx, param, value):
    cfg = config.from_path(value)
    return config.setup_crypt(cfg)
