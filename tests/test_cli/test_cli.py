import logging
import os
import tarfile
import tempfile

import click
import pytest
import yaml

from passpie.cli import cli


def test_cli_verbose_sets_level_debug_when_true(irunner, mocker):
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner.invoke(cli, ["--verbose", "list"])
    assert result.exit_code == 0, result.output
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.INFO


def test_cli_verbose_sets_level_critical_when_false(irunner, mocker):
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is False


def test_cli_debug_sets_level_debug_when_debug_set(irunner, mocker):
    environ_variables = {"PASSPIE_DEBUG": "true"}
    mocker.patch.dict("passpie.cli.os.environ", environ_variables)
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.DEBUG


def test_cli_verbose_sets_level_info_when_verbose_environ_variable_set(irunner, mocker):
    environ_variables = {"PASSPIE_VERBOSE": "true"}
    mocker.patch.dict("passpie.cli.os.environ", environ_variables)
    mock_set_level = mocker.patch("passpie.cli.logger.setLevel")
    result = irunner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert mock_set_level.called is True
    args, _ = mock_set_level.call_args
    assert args[0] == logging.INFO
