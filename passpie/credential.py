import re


def split_fullname(fullname):
    rgx = re.compile(r"(?P<login>.*)@(?P<name>.*)")
    try:
        name = rgx.match(fullname).group("name")
        login = rgx.match(fullname).group("login")
    except AttributeError:
        raise ValueError("Not a valid name")
    return login if login else "_", name
