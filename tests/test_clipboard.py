import pytest

from passpie import clipboard


def test_clipboard_on_osx_ensure_commands(mocker):
    mocker.patch('passpie.clipboard.process.call')
    mock_ensure_commands = mocker.patch('passpie.clipboard.ensure_commands')
    commands = clipboard.OSX_COMMANDS

    clipboard._copy_osx('text')

    mock_ensure_commands.assert_called_once_with(commands)


def test_clipboard_on__ensure_commands(mocker):
    mocker.patch('passpie.clipboard.process.call')
    mock_ensure_commands = mocker.patch('passpie.clipboard.ensure_commands')
    commands = clipboard.LINUX_COMMANDS

    clipboard._copy_linux('text')

    mock_ensure_commands.assert_called_once_with(commands)


def test_copy_calls_copy_osx_when_on_darwin_system(mocker):
    mocker.patch('passpie.clipboard.process.call')
    mocker.patch('passpie.clipboard.platform.system', return_value='Darwin')
    mock_copy_osx = mocker.patch('passpie.clipboard._copy_osx')
    mock_copy_linux = mocker.patch('passpie.clipboard._copy_linux')
    mock_copy_windows = mocker.patch('passpie.clipboard._copy_windows')

    clipboard.copy('text')

    assert mock_copy_osx.called is True
    assert mock_copy_linux.called is False
    assert mock_copy_windows.called is False
    mock_copy_osx.assert_called_once_with('text', 0)


def test_copy_calls_copy_linux_when_on_linux_system(mocker):
    mocker.patch('passpie.clipboard.process.call')
    mocker.patch('passpie.clipboard.platform.system', return_value='Linux')
    mock_copy_osx = mocker.patch('passpie.clipboard._copy_osx')
    mock_copy_linux = mocker.patch('passpie.clipboard._copy_linux')
    mock_copy_windows = mocker.patch('passpie.clipboard._copy_windows')

    clipboard.copy('text')

    assert mock_copy_linux.called is True
    assert mock_copy_osx.called is False
    assert mock_copy_windows.called is False
    mock_copy_linux.assert_called_once_with('text', 0)


def test_copy_calls_copy_windows_when_on_windows_system(mocker):
    mocker.patch('passpie.clipboard.process.call')
    mocker.patch('passpie.clipboard.platform.system', return_value='Windows')
    mock_copy_osx = mocker.patch('passpie.clipboard._copy_osx')
    mock_copy_linux = mocker.patch('passpie.clipboard._copy_linux')
    mock_copy_windows = mocker.patch('passpie.clipboard._copy_windows')

    clipboard.copy('text')

    assert mock_copy_windows.called is True
    assert mock_copy_osx.called is False
    assert mock_copy_linux.called is False
    mock_copy_windows.assert_called_once_with('text', 0)


def test_copy_calls_copy_cygwin_when_on_cygwin_system(mocker):
    mocker.patch('passpie.clipboard.platform.system', return_value='cygwin system')
    mock_copy_cygwin = mocker.patch('passpie.clipboard._copy_cygwin')
    text = 's3cr3t'

    clipboard.copy(text)

    assert mock_copy_cygwin.called
    mock_copy_cygwin.assert_called_once_with(text, 0)


def test_logs_error_msg_when_platform_not_supported(mocker):
    mocker.patch('passpie.clipboard.platform.system', return_value='unknown')
    mock_logger = mocker.patch('passpie.clipboard.logging')

    clipboard.copy('text')
    assert mock_logger.error.called
    msg = "platform 'unknown' copy to clipboard not supported"
    mock_logger.error.assert_called_once_with(msg)


def test_ensure_commands_logs_error_when_command_not_found(mocker):
    mocker.patch('passpie.clipboard.which', return_value=False)
    mock_logging = mocker.patch('passpie.clipboard.logging')
    clipboard.ensure_commands(clipboard.LINUX_COMMANDS)

    assert mock_logging.error.called


def test_ensure_commands_returns_command(mocker):
    commands = {'xclip': ['xclip']}
    mocker.patch('passpie.clipboard.which', return_value=True)

    result = clipboard.ensure_commands(commands)

    assert result == commands['xclip']


def test_clear_sleep_for_delay_seconds(mocker):
    mocker.patch('passpie.clipboard.process')
    mocker.patch('passpie.clipboard.sys.stdout')
    mocker.patch('passpie.clipboard.print', create=True)
    mock_time = mocker.patch('passpie.clipboard.time')

    clipboard.clean('some command', delay=5)
    assert mock_time.sleep.call_count == 5


def test_clear_calls_command_to_clear_with_whitespace_char(mocker):
    mocker.patch('passpie.clipboard.sys.stdout')
    mocker.patch('passpie.clipboard.print', create=True)
    mocker.patch('passpie.clipboard.time')
    mock_process = mocker.patch('passpie.clipboard.process')

    clipboard.clean('some command', delay=5)
    assert mock_process.call.called
    mock_process.call.assert_called_once_with('some command', input='\b')


def test_clear_is_called_when_clear_is_passed_to_copy_osx(mocker):
    mocker.patch('passpie.clipboard.ensure_commands', return_value='command')
    mocker.patch('passpie.clipboard.process')
    mock_clean = mocker.patch('passpie.clipboard.clean')

    clipboard._copy_osx('text', clear=5)
    assert mock_clean.called
    mock_clean.assert_called_once_with('command', delay=5)


def test_clear_is_called_when_clear_is_passed_to_copy_linux(mocker):
    mocker.patch('passpie.clipboard.ensure_commands', return_value='command')
    mocker.patch('passpie.clipboard.process')
    mock_clean = mocker.patch('passpie.clipboard.clean')

    clipboard._copy_linux('text', clear=5)
    assert mock_clean.called
    mock_clean.assert_called_once_with('command', delay=5)
