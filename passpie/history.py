from functools import wraps
import logging
import os

from . import process
from ._compat import which
from .utils import touch


logger = logging.getLogger(__name__)


def ensure_git(return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if which('git'):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.debug(str(e))
            else:
                logger.debug('git is not installed')
            return return_value
        return wrapper
    return decorator


class Repository(object):

    def __init__(self, path):
        self.path = path

    @ensure_git()
    def init(self, message='Initialized git repository'):
        cmd = ['git', 'init', self.path]
        touch(os.path.join(self.path, '.gitkeep'))
        process.call(cmd, cwd=self.path)
        self.add(all=True)
        self.commit(message)

    @ensure_git()
    def add(self, all=True):
        cmd = ['git', 'add', '--all', '.']
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def commit(self, message, add=True):
        if add:
            self.add()
        cmd = ['git', 'commit', '-m', message]
        process.call(cmd, cwd=self.path)

    @ensure_git(return_value=[])
    def commit_list(self):
        cmd = ['git', 'log', '--reverse', '--pretty=format:%s']
        output, _ = process.call(cmd, cwd=self.path)
        return output.splitlines()
