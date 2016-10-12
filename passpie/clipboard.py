"""
parts of this code from pyperclip: https://github.com/asweigart/pyperclip
"""
import ctypes
import logging
import platform
import time
import sys

from . import process
from ._compat import unicode, is_python2, which


LINUX_COMMANDS = {
    'xsel': ['xsel', '-ibps'],
    'xclip': ['xclip', '-i']
}

OSX_COMMANDS = {
    'pbcopy': ['pbcopy', 'w']
}


def ensure_commands(commands):
    for command_name, command in commands.items():
        if which(command_name) and command:
            return command
    else:
        logging.error('missing commands: ', ' or '.join(commands))


def clean(command, delay):
    print('Password copied to clipboard. Waiting for {}s to clear clipboard'.format(delay))
    for dot in ['.' for _ in range(delay)]:
        sys.stdout.write(dot)
        sys.stdout.flush()
        time.sleep(1)
    else:
        process.call(command, input='\b')
        print('')


def _copy_windows(text, clear=0):
    GMEM_DDESHARE = 0x2000
    CF_UNICODETEXT = 13
    d = ctypes.windll  # cdll expects 4 more bytes in user32.OpenClipboard(0)
    if not isinstance(text, unicode):
        text = text.decode('mbcs')

    d.user32.OpenClipboard(0 if is_python2() else None)

    d.user32.EmptyClipboard()
    hCd = d.kernel32.GlobalAlloc(GMEM_DDESHARE, len(text.encode('utf-16-le')) + 2)
    pchData = d.kernel32.GlobalLock(hCd)
    ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), text)
    d.kernel32.GlobalUnlock(hCd)
    d.user32.SetClipboardData(CF_UNICODETEXT, hCd)
    d.user32.CloseClipboard()


def _copy_cygwin(text, clear=0):
    GMEM_DDESHARE = 0x2000
    CF_UNICODETEXT = 13
    d = ctypes.cdll
    if not isinstance(text, unicode):
        text = text.decode('mbcs')
    d.user32.OpenClipboard(0)
    d.user32.EmptyClipboard()
    hCd = d.kernel32.GlobalAlloc(GMEM_DDESHARE,
                                 len(text.encode('utf-16-le')) + 2)
    pchData = d.kernel32.GlobalLock(hCd)
    ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), text)
    d.kernel32.GlobalUnlock(hCd)
    d.user32.SetClipboardData(CF_UNICODETEXT, hCd)
    d.user32.CloseClipboard()


def _copy_osx(text, clear=0):
    command = ensure_commands(OSX_COMMANDS)
    process.call(command, input=text)
    if clear:
        clean(command, delay=clear)


def _copy_linux(text, clear=0):
    command = ensure_commands(LINUX_COMMANDS)
    process.call(command, input=text)
    if clear:
        clean(command, delay=clear)


def copy(text, clear=0):
    platform_name = platform.system().lower()
    if platform_name == 'darwin':
        _copy_osx(text, clear)
    elif platform_name == 'linux':
        _copy_linux(text, clear)
    elif platform_name == 'windows':
        _copy_windows(text, clear)
    elif 'cygwin' in platform_name.lower():
        _copy_cygwin(text, clear)
    else:
        msg = "platform '{}' copy to clipboard not supported".format(
            platform_name)
        logging.error(msg)
        return
    logging.debug('text copied to clipboard')
