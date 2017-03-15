from tempfile import mkdtemp
import functools
import os

from .exceptions import FileExistsError
from .utils import logger, safe_join, which
from .proc import run
from .gpg import DEFAULT_EMAIL, DEFAULT_NAME


def ensure_git(repository_exists=True):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            if not which("git"):
                logger.info("git not found. -- mocking call --")
            elif (repository_exists is True and
                  not os.path.exists(safe_join(self.path, ".git"))):
                logger.info("git repository not found. -- mocking call --")
            else:
                return f(self, *args, **kwargs)
            return self
        return wrapper
    return decorator


def parse_remote(arg):
    origin, branch = arg.split("/")
    return origin, branch


def clone(url, dest=None, depth=None):
    if dest and os.path.exists(dest):
        raise FileExistsError('Destination already exists: %s' % dest)
    dest = dest if dest else mkdtemp()
    cmd = ['git', 'clone', url, dest]
    if depth:
        cmd += ['--depth', depth]
    run(cmd)
    return dest


class Repo(object):

    def __init__(self, path):
        self.path = path
        self.author = "{} <{}>".format(DEFAULT_NAME, DEFAULT_EMAIL)

    @ensure_git(repository_exists=False)
    def init(self):
        logger.info("runnint git init")
        run(["git", "init"], cwd=self.path)
        return self

    @ensure_git()
    def push(self, remote="origin", branch="HEAD"):
        logger.info("git pushing")
        run(["git", "push", remote, branch], cwd=self.path)
        return self

    @ensure_git()
    def commit(self, message):
        logger.info("git commiting in repo")
        run(["git", "add", "."], cwd=self.path)
        run(["git", "commit", "--author", self.author, "-m", message], cwd=self.path)
        return self
