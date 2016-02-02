from copy import deepcopy
import pytest

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
def config(mockie):
    import passpie.config
    config = mockie.patch('passpie.cli.config')
    config.load.return_value = passpie.config.DEFAULT
    return config


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
    init_kwargs = {}
    marker = request.node.get_marker('runner_setup')
    if marker:
        init_kwargs = marker.kwargs
    return CliRunner(**init_kwargs)


@pytest.yield_fixture
def irunner(runner):
    """
    Instance of `click.testing.CliRunner` with automagically `isolated_filesystem()` called.
    """
    with runner.isolated_filesystem():
        yield runner


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'runner_setup(**kwargs): Pass kwargs to `click.testing.CliRunner` initialization.'
    )
