from subprocess import Popen, PIPE

from ._compat import *


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
    kwargs.setdefault('stdout', PIPE)
    kwargs.setdefault('stderr', PIPE)
    kwargs.setdefault('stdin', PIPE)
    kwargs.setdefault('shell', False)
    kwargs_input = kwargs.pop('input', None)

    with Proc(*args, **kwargs) as proc:
        output, error = proc.communicate(input=kwargs_input)
        if isinstance(output, basestring):
            output = output.decode('utf-8')
        return output, error
