"""
parts of this code from pyperclip: https://github.com/asweigart/pyperclip
"""

from subprocess import Popen, PIPE
import ctypes
import platform

from ._compat import which, is_python2
from .utils import logger


text_type = unicode if is_python2() else str

LINUX_COMMANDS = {
    'xsel': ['xsel', '-p'],
    'xclip': ['xclip', '-i']
}

OSX_COMMANDS = {
    'pbcopy': ['pbcopy', 'w']
}


def _copy_windows(text):
    GMEM_DDESHARE = 0x2000
    CF_UNICODETEXT = 13
    d = ctypes.windll  # cdll expects 4 more bytes in user32.OpenClipboard(0)
    if not isinstance(text, text_type):
        text = text.decode('mbcs')

    d.user32.OpenClipboard(0 if is_python2() else None)

    d.user32.EmptyClipboard()
    hCd = d.kernel32.GlobalAlloc(GMEM_DDESHARE, len(text.encode('utf-16-le')) + 2)
    pchData = d.kernel32.GlobalLock(hCd)
    ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), text)
    d.kernel32.GlobalUnlock(hCd)
    d.user32.SetClipboardData(CF_UNICODETEXT, hCd)
    d.user32.CloseClipboard()


def _copy_cygwin(text):
    GMEM_DDESHARE = 0x2000
    CF_UNICODETEXT = 13
    d = ctypes.cdll
    if not isinstance(text, text_type):
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


def ensure_commands(commands):
    for command_name, command in commands.items():
        if which(command_name) and command:
            return command
    else:
        raise SystemError('missing commands: ',
                          ' or '.join(commands))


def _copy_osx(text):
    command = ensure_commands(OSX_COMMANDS)
    p = Popen(command, stdin=PIPE, close_fds=True)
    p.communicate(input=text)


def _copy_linux(text):
    command = ensure_commands(LINUX_COMMANDS)
    p = Popen(command, stdin=PIPE, close_fds=True)
    p.communicate(input=text)


def copy(text):
    if platform.system() == 'Darwin':
        _copy_osx(text)
    elif platform.system() == 'Linux':
        _copy_linux(text)
    elif platform.system() == 'Windows':
        _copy_windows(text)
    elif 'cygwin' in platform.system().lower() == '':
        _copy_cygwin(text)
    else:
        raise SystemError('system not supported')
