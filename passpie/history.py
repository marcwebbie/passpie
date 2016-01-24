from functools import wraps
import logging

from . import process
from ._compat import which


def ensure_git(return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if which('git'):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.debug(str(e))
            else:
                logging.debug('git is not installed')
            return return_value
        return wrapper
    return decorator


class Repository(object):

    def __init__(self, path):
        self.path = path

    @ensure_git()
    def init(self):
        cmd = ['git', 'init', self.path]
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def add(self, all=False):
        cmd = ['git', 'add', '--all', '.']
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def commit(self, message, add=True):
        if add:
            self.add(all=True)
        cmd = ['git', 'commit', '-m', message]
        process.call(cmd, cwd=self.path)

    @ensure_git(return_value=[])
    def commit_list(self):
        cmd = ['git', 'log', '--reverse', '--pretty=format:%s']
        output, _ = process.call(cmd, cwd=self.path)
        return output.splitlines()

    @ensure_git(return_value=[])
    def sha_list(self):
        cmd = ['git', 'log', '--reverse', '--pretty=format:%h']
        output, _ = process.call(cmd, cwd=self.path)
        return output.splitlines()

    @ensure_git()
    def reset(self, to_index):
        try:
            sha = self.sha_list()[to_index]
        except IndexError:
            logging.info('commit on index "{}" not found'.format(to_index))

        cmd = ['git', 'reset', '--hard', sha]
        process.call(cmd, cwd=self.path)
