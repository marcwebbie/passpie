from errno import EEXIST
import os
import sys
from functools import partial

is_python2 = lambda: sys.version_info < (3,)

if is_python2():
    BUILTINS_NAME = "__builtin__"

    def input(prompt):
        return raw_input(prompt).decode("UTF-8")

    def makedirs(name, exist_ok=False):
        try:
            os.makedirs(name=name)
        except OSError as e:
            if not exist_ok or e.errno != EEXIST or not os.path.isdir(name):
                raise
else:
    BUILTINS_NAME = "builtins"
    input = input
    makedirs = partial(os.makedirs)
