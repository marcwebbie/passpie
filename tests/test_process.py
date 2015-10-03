import pytest
from passpie.process import Proc, call


@pytest.fixture
def mock_popen(mocker):
    return mocker.patch('passpie.process.Popen')


def test_call_uses_proc_communicate_with_input(mocker, mock_popen):
    MockProc = mocker.patch('passpie.process.Proc')
    MockProc().__enter__.return_value.communicate.return_value = ('', '')
    call(['echo', 'hello'])
    assert MockProc().__enter__.called is True
    assert MockProc().__exit__.called is True


def test_call_output_and_error_are_utf8_decoded(mocker, mock_popen):
    MockProc = mocker.patch('passpie.process.Proc')
    output = mocker.MagicMock()
    error = mocker.MagicMock()
    MockProc().__enter__.return_value.communicate.return_value = (output, error)

    result_output, result_error = call(['echo', 'hello'])

    assert output.decode.called is True
    assert error.decode.called is True
    assert result_output == output.decode('utf-8')
    assert result_error == error.decode('utf-8')


def test_call_output_and_error_doesnt_decode_in_case_of_unicode(mocker, mock_popen):
    MockProc = mocker.patch('passpie.process.Proc')
    output = mocker.MagicMock()
    error = mocker.MagicMock()
    output.decode.side_effect = AttributeError
    error.decode.side_effect = AttributeError
    MockProc().__enter__.return_value.communicate.return_value = (output, error)

    result_output, result_error = call(['echo', 'hello'])

    assert result_output == output
    assert result_error == error
