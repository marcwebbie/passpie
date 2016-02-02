from functools import wraps
import logging

from . import process
from .utils import which, tempdir
from ._compat import *


def ensure_git(return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if which('git'):
                return func(*args, **kwargs)
            else:
                logging.error('git is not installed')
            return return_value
        return wrapper
    return decorator


@ensure_git()
def clone(url, dest=None, depth=None):
    if dest and os.path.exists(dest):
        raise FileExistsError('Destination already exists: %s' % dest)
    dest = dest if dest else tempdir()
    cmd = ['git', 'clone', url, dest]
    if depth:
        cmd += ['--depth', depth]
    process.call(cmd)
    return dest


class Repository(object):

    def __init__(self, path, autopull=None, autopush=None):
        self.path = path
        self.autopush = autopush
        self.autopull = autopull
        if autopull:
            self.pull_rebase(*autopull)

    @ensure_git()
    def init(self):
        cmd = ['git', 'init', self.path]
        process.call(cmd)

    @ensure_git()
    def pull_rebase(self, remote='origin', branch='master'):
        cmd = ['git', 'pull', '--rebase', remote, branch]
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def push(self, remote='origin', branch='master'):
        cmd = ['git', 'push', remote, branch]
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def add(self, all=False):
        if all is True:
            cmd = ['git', 'add', '--all', '.']
        else:
            cmd = ['git', 'add', '.']
        process.call(cmd, cwd=self.path)

    @ensure_git()
    def commit(self, message, add=True):
        if add:
            self.add(all=True)
        cmd = ['git', 'commit', '-m', message]
        process.call(cmd, cwd=self.path)
        if self.autopush:
            self.push()

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
            cmd = ['git', 'reset', '--hard', sha]
            process.call(cmd, cwd=self.path)
        except IndexError:
            logging.info('commit on index "{}" not found'.format(to_index))
