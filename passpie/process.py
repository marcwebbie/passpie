import logging
import os
from subprocess import Popen, PIPE

from ._compat import basestring


DEVNULL = open(os.devnull, 'w')


class Proc(Popen):

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


def call(*args, **kwargs):
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        stderr = PIPE
    else:
        stderr = DEVNULL

    kwargs.setdefault('stderr', stderr)
    kwargs.setdefault('stdout', PIPE)
    kwargs.setdefault('stdin', PIPE)
    kwargs.setdefault('shell', False)
    kwargs_input = kwargs.pop('input', None)

    with Proc(*args, **kwargs) as proc:
        output, error = proc.communicate(input=kwargs_input)
        try:
            output = output.decode('utf-8')
            error = error.decode('utf-8')
        except AttributeError:
            pass
        return output, error
