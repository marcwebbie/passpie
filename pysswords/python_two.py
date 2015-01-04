import os
import sys
from functools import partial

if sys.version_info < (3,2):
    from distutils.dir_util import mkpath as makedirs
else:
    makedirs = partial(os.makedirs, exist_ok=True)
