from functools import partial
from copy import deepcopy
import tempfile

import pytest

from passpie.crypt import get_default_recipient, import_keys
from passpie import config
from . import helpers


@pytest.fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


@pytest.fixture
def mockie(mocker, mock_open):
    mocker.mock_open = mock_open
    return mocker


@pytest.fixture
def mock_config(mocker):
    class Config(object):
        def __init__(self, overrides={}):
            self.overrides = overrides
            self.values = config.DEFAULT.copy()
            self.values['path'] = tempfile.NamedTemporaryFile().name
            self.values.update(overrides)
            mocker.patch.dict('passpie.validators.config.DEFAULT',
                              self.values, clear=True)
            mocker.patch('passpie.config.read', self.read)
            mocker.patch('passpie.config.setup_crypt', self.setup_crypt)

        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(self, *args, **kwargs):
            pass

        def __getitem__(self, name):
            return self.values[name]

        def read(self, *args, **kwargs):
            return self.overrides

        def setup_crypt(self, *args, **kwargs):
            keysfile = tempfile.NamedTemporaryFile(mode="w")
            keysfile.write(helpers.KEYS)
            configuration = self.values
            configuration['homedir'] = tempfile.mkdtemp()
            import_keys(keysfile.name, configuration['homedir'])
            configuration['recipient'] = get_default_recipient(configuration['homedir'])
            return configuration

    return Config


@pytest.fixture
def creds(mocker, faker):
    """Mock credentials to database"""
    class CredentialFaker(object):
        def make(self, number=1):
            credentials = []
            for _ in range(number):
                credential = {
                    'name': faker.domain_name(),
                    'login': faker.user_name(),
                    'password': faker.md5(),
                    'comment': faker.word(),
                }
                credential['fullname'] =  u"{}@{}".format(
                    credential['login'], credential['name'])
                credentials.append(credential)
            mocker.patch('passpie.cli.Database.credentials',
                         return_value=deepcopy(credentials))
            return credentials
    return CredentialFaker()


@pytest.fixture
def runner(request, mocker):
    """
    Instance of `click.testing.CliRunner`. Can be configured with `@pytest.mark.runner_setup`
    @pytest.mark.runner_setup(charset='cp1251')
    def test_something(cli_runner):
        ...
    """
    from click.testing import CliRunner
    mocker.patch('passpie.cli.create_keys', helpers.create_keys)
    mocker.patch('passpie.cli.ensure_dependencies')
    mocker.patch('passpie.database.Repository')
    init_kwargs = {}
    marker = request.node.get_marker('runner_setup')
    if marker:
        init_kwargs = marker.kwargs
    return CliRunner(**init_kwargs)


@pytest.yield_fixture
def irunner(mocker, runner):
    """
    Instance of `click.testing.CliRunner` with automagically `isolated_filesystem()` called.
    """
    with runner.isolated_filesystem():
        runner.invoke = partial(runner.invoke, catch_exceptions=False)
        yield runner
