from .history import clone
from . import config


def validate_config(ctx, param, value):
    overrides = {k: v for k, v in ctx.params.items() if v}
    configuration = {}
    configuration.update(config.DEFAULT)                             # Default configuration
    configuration.update(config.read(config.HOMEDIR, '.passpierc'))  # Global configuration
    configuration.update(config.read(configuration['path']))         # Local configuration
    if value:
        configuration.update(config.read(value))                     # Options configuration
    configuration.update(overrides)                                  # Command line options

    if config.is_repo_url(configuration['path']) is True:
        temporary_path = clone(configuration['path'], depth="1")
        configuration.update(config.read(temporary_path))  # Read cloned config
        configuration['path'] = temporary_path

    configuration = config.setup_crypt(configuration)
    return configuration
