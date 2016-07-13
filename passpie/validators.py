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


def validate_config(ctx, param, value):
    overrides = {k: v for k, v in ctx.params.items() if v}
    configuration = {}
    configuration.update(config.DEFAULT)                             # Default configuration
    configuration.update(config.read(config.HOMEDIR, '.passpierc'))  # Global configuration
    if value:
        configuration.update(config.read(value))                     # Options configuration
    configuration.update(overrides)                                  # Command line options

    if config.is_repo_url(configuration['path']) is True:
        temporary_path = clone(configuration['path'], depth="1")
        configuration['path'] = temporary_path

    configuration.update(config.read(configuration['path']))
    configuration = config.setup_crypt(configuration)
    return configuration
