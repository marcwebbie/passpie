# -*- coding: utf-8 -*-
import pytest
from passpie.proc import Proc, run, DEVNULL, PIPE


@pytest.fixture
def mock_popen(mocker):
    return mocker.patch('passpie.proc.Popen')


def test_call_uses_proc_communicate_with_input(mocker, mock_popen):
    MockProc = mocker.patch('passpie.proc.Proc')
    MockProc().__enter__.return_value.communicate.return_value = ('', '')
    run(['echo', 'hello'])
    assert MockProc().__enter__.called is True
    assert MockProc().__exit__.called is True


def test_call_sets_stderr_as_pipe_when_logger_level_is_set_to_debug(mocker, mock_popen):
    MockProc = mocker.patch('passpie.proc.Proc')
    MockProc().__enter__.return_value.communicate.return_value = ('', '')
    mock_logging = mocker.patch('passpie.proc.logging')
    mock_logging.getLogger().getEffectiveLevel.return_value = 10
    mock_logging.DEBUG = 10

    run(['echo', 'hello'])
    args, kwargs = MockProc.call_args
    assert kwargs['stderr'] == PIPE


def test_call_output_and_error_are_utf8_decoded(mocker, mock_popen):
    MockProc = mocker.patch('passpie.proc.Proc')
    output = mocker.MagicMock()
    error = mocker.MagicMock()
    MockProc().__enter__.return_value.communicate.return_value = (output, error)

    response = run(['echo', 'hello'])

    assert output.decode.called is True
    assert error.decode.called is True
    assert response.std_out == output.decode('utf-8')
    assert response.std_err == error.decode('utf-8')


def test_call_output_and_error_doesnt_decode_in_case_of_unicode(mocker, mock_popen):
    MockProc = mocker.patch('passpie.proc.Proc')
    output = mocker.MagicMock()
    error = mocker.MagicMock()
    output.decode.side_effect = AttributeError
    error.decode.side_effect = AttributeError
    MockProc().__enter__.return_value.communicate.return_value = (output, error)

    response = run(['echo', 'hello'])

    assert response.std_out == output
    assert response.std_err == error


def test_call_handles_unicode_input(mocker, mock_popen):
    response = run(['echo', "josé"])
    assert response.returncode == 0
