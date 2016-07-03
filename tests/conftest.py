from functools import partial

import pytest
from click.testing import CliRunner


@pytest.yield_fixture
def irunner(mocker):
    """
    Instance of `click.testing.CliRunner` with automagically `isolated_filesystem()` called.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke = partial(runner.invoke, catch_exceptions=False)
        yield runner
