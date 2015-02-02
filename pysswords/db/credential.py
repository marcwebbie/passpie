from collections import namedtuple
import os
import re
import shutil
import yaml


Credential = namedtuple("Credential", "name login password comment")


class CredentialExistsError(Exception):
    pass


class CredentialNotFoundError(Exception):
    pass


def expandpath(path, name, login):
    return os.path.join(path, name, "{}.pyssword".format(login))


def content(credential):
    return yaml.dump(credential)


def asdict(credential):
    return credential._asdict()


def asstring(credential):
    return "{} {} {}".format(
        credential.name,
        credential.login,
        credential.comment
    )


def exists(path, name, login):
    return True if os.path.isfile(expandpath(path, name, login)) else False


def clean(path, name, login):
    if exists(path, name, login):
        os.remove(expandpath(path, name, login))
    credential_dir = os.path.dirname(expandpath(path, name, login))
    if not os.listdir(credential_dir):
        shutil.rmtree(credential_dir)


def splitname(fullname):
    rgx = re.compile(r"(?:(?P<login>.+?@?.+)?@)?(?P<name>.+)")
    if rgx.match(fullname):
        name = rgx.match(fullname).group("name")
        login = rgx.match(fullname).group("login")
        return name, login
    else:
        raise ValueError("Not a valid name")


def asfullname(name, login):
    return "{}@{}".format(login if login else "", name)
