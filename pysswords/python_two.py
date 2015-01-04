from errno import EEXIST
import os
import sys
from functools import partial


if sys.version_info < (3,):
    def makedirs(name, mode=0777, exist_ok=False):
        try:
            os.makedirs(name=name, mode=mode)
        except OSError as e:
            if not exist_ok or e.errno != EEXIST or not os.path.isdir(name):
                raise
else:
    makedirs = partial(os.makedirs)
