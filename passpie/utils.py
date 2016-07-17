"""
General utilities
"""

from contextlib import contextmanager
from collections import namedtuple
import bz2
import errno
import gzip
import logging
import os
import re
import shutil
import sys
import tarfile
import tempfile
import time
import zipfile

from faker import Faker
from tinydb.storages import touch as _touch
import pyperclip
import rstr
import yaml


HOME = os.path.expanduser("~")

logger = logging.getLogger('passpie')
LOGGER_HANDLER = logging.StreamHandler()
LOGGER_FORMATTER = logging.Formatter("%(levelname)s:passpie.%(module)s:%(message)s")
LOGGER_HANDLER.setFormatter(LOGGER_FORMATTER)
logger.addHandler(LOGGER_HANDLER)
logger.setLevel(logging.CRITICAL)


Archive = namedtuple("Archive", "path source format")


def safe_join(*paths):
    return os.path.join(*[os.path.expanduser(p) for p in paths])


def yaml_dump(data, path=None):
    content = yaml.safe_dump(data, default_flow_style=False)
    if path:
        with open(path, "w") as yamlfile:
            yamlfile.write(content)
    else:
        return content


def yaml_to_python(data):
    try:
        return yaml.safe_load("[%s]" % data)[0]
    except yaml.scanner.ScannerError:
        return "{}".format(data)


def touch(path):
    return _touch(path)


def yaml_load(path, ensure=False):
    yaml_content = {}
    try:
        with open(path) as yamlfile:
            yaml_content = yaml.safe_load(yamlfile.read())
    except IOError:
        logger.info(u'YAML file "%s" not found', path)
    except yaml.scanner.ScannerError as exc:
        raise ValueError(u'Malformed YAML file: {}'.format(exc))

    if not yaml_content and ensure is True:
        raise RuntimeError("YAML content is empty and ensure is True")
    else:
        return yaml_content


def genpass(pattern=None, length=32):
    """Generate random password
    """
    if pattern:
        try:
            return rstr.xeger(pattern)
        except re.error as exc:
            raise ValueError(str(exc))
        except KeyError:
            # Error in python 3.5, rstr does not support
            pass

    return Faker().password(length=length)


def which(*binaries):
    try:
        from shutil import which as _which
    except ImportError:
        from distutils.spawn import find_executable as _which

    for binary in binaries:
        path = _which(binary)
        if path:
            realpath = os.path.realpath(path)
            return realpath
    return None


def copy_to_clipboard(text, timeout):
    pyperclip.copy(text)
    if timeout:
        for dot in ['.' for _ in range(timeout)]:
            sys.stdout.write(dot)
            sys.stdout.flush()
            time.sleep(1)
        pyperclip.copy("\b")
        sys.stdout.write("\n")


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def make_archive(src, dest, dest_format):
    if dest_format == "git":
        return
    elif dest_format == "dir":
        tpath = src
    else:
        tfile = tempfile.NamedTemporaryFile()
        tpath = shutil.make_archive(tfile.name, dest_format, src)
    shutil.move(tpath, dest)


def find_compression_type(filename):
    with gzip.GzipFile(filename) as gzfile:
        try:
            gzfile.read()
            return "gz"
        except IOError:
            pass

    with bz2.BZ2File(filename) as bzfile:
        try:
            bzfile.read()
            return "bz2"
        except IOError:
            pass


def is_git_url(path):
    regex = re.compile(
        r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?'
    )
    return bool(path and regex.match(path))


def get_archive_format(path):
    if not path or not os.path.exists(path):
        raise IOError("path not found: %s" % path)
    elif os.path.isdir(path):
        return "dir"
    elif is_git_url(path):
        return "git"
    try:
        if tarfile.is_tarfile(path):
            compression = find_compression_type(path)
            if compression == "gz":
                return "gztar"
            elif compression == "bz2":
                return "bztar"
            else:
                return "tar"
        elif zipfile.is_zipfile(path):
            return "zip"
    except (IOError, TypeError):
        raise IOError("unrecognized source path: %s" % path)


def extract(src, src_format):
    from .git import clone
    if src_format in ["dir"]:
        dest = src
    if src_format in ["git"]:
        dest = clone(src)
    elif src_format in ("tar", "gztar", "bztar", "zip"):
        dest = tempfile.mkdtemp()
        if src_format == "zip":
            with zipfile.ZipFile(src) as zipf:
                zipf.extractall(dest)
        with tarfile.open(src) as tarf:
            tarf.extractall(dest)
    return dest


def cat(path):
    with open(path) as catfile:
        return catfile.read()


def find_db_root(path):
    for root, _, files in os.walk(path):
        if ".passpie" in files or "credentials.yml" in files:
            return root
    raise IOError("Path is not a passpie database: {}".format(path))


@contextmanager
def auto_archive(source):
    source_format = get_archive_format(source)
    if source_format == "dir":
        path = find_db_root(source)
        yield Archive(path, source, source_format)
    else:
        path = find_db_root(extract(source, source_format))
        yield Archive(path, source, source_format)
        make_archive(path, source, source_format)
