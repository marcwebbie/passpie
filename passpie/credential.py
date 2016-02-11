import re


def split_fullname(fullname):
    regex = re.compile(r'(?:(?P<login>.+?(?:\@.+?)?)@(?P<name>.+?$))')
    regex_name_only = re.compile(r'(?P<at>@)?(?P<name>.+?$)')

    if regex.match(fullname):
        mobj = regex.match(fullname)
    elif regex_name_only.match(fullname):
        mobj = regex_name_only.match(fullname)
    else:
        raise ValueError("Not a valid name")

    if mobj.groupdict().get('at'):
        login = ""
    else:
        login = mobj.groupdict().get('login')
    name = mobj.groupdict().get("name")

    return login, name


def make_fullname(login, name):
    fullname = u"{}@{}".format("" if login is None else login, name)
    return fullname
