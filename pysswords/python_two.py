from errno import EEXIST
import os
import sys
from functools import partial
try:
    from unittest.mock import patch, Mock
    from io import StringIO
except ImportError:
    # backwards compatbility with Python2
    from mock import patch, Mock
    from StringIO import StringIO


if sys.version_info < (3,):
    def makedirs(name, exist_ok=False):
        try:
            os.makedirs(name=name)
        except OSError as e:
            if not exist_ok or e.errno != EEXIST or not os.path.isdir(name):
                raise
else:
    makedirs = partial(os.makedirs)

if sys.version_info >= (3,):
    BUILTINS_NAME = "builtins"
else:
    BUILTINS_NAME = "__builtin__"
