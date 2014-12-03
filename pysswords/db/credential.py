from collections import namedtuple


Credential = namedtuple(
    "Credential",
    ["name", "login", "password", "login_url", "description"]
)
