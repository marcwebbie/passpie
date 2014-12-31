from collections import namedtuple
import os
import yaml


Credential = namedtuple("Credential", "name login password comment")


class CredentialExistsError(ValueError):
    pass


def expandpath(path, credential):
    return os.path.join(path,
                        credential.name,
                        "{}.pyssword".format(credential.login))


def content(credential):
    return yaml.dump(credential)
