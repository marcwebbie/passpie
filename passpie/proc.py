"""
Process wrapper
"""
from collections import namedtuple
from subprocess import Popen, PIPE
import logging
import os


from ._compat import *
from .utils import logger


DEVNULL = open(os.devnull, 'w')

Response = namedtuple("Response", "cmd std_out std_err returncode")


class Proc(Popen):
    """Wrapper on Subprocess.POPEN"""

    def communicate(self, **kwargs):
        if kwargs.get('input') and isinstance(kwargs['input'], basestring):
            kwargs['input'] = kwargs['input'].encode('utf-8')
        return super(Proc, self).communicate(**kwargs)

    def __exit__(self, *args, **kwargs):
        if hasattr(super(Proc, self), '__exit__'):
            super(Proc, self).__exit__(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        if hasattr(super(Proc, self), '__enter__'):
            return super(Proc, self).__enter__(*args, **kwargs)
        return self


def run(*args, **kwargs):
    data = kwargs.pop('data', None)
    kwargs.setdefault('shell', False)
    kwargs.setdefault('pipe', True)
    kwargs.setdefault('stdin', PIPE)
    if kwargs.pop("pipe") is True:
        kwargs.setdefault('stderr', PIPE)
        kwargs.setdefault('stdout', PIPE)

    with Proc(*args, **kwargs) as proc:
        std_out, std_err = proc.communicate(input=data)
        cmd = args[0]
        returncode = proc.returncode
        try:
            std_out = std_out.decode('utf-8')
            std_err = std_err.decode('utf-8')
        except AttributeError:
            pass
        response = Response(cmd, std_out, std_err, returncode)

    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("run(command):%s", " ".join(cmd))
        if std_err and std_err.strip():
            logger.debug(std_err)
        if response.returncode != 0:
            logger.debug("run(command):error(%s):%s", response.returncode, response)
    return response
