import json


def onepassword(dbfile):
    with open(dbfile) as f:
        contents = f.read().split("\n")
        entries = [json.loads(cred) for cred in contents
                   if cred.startswith("{")]
    credentials = []
    for entry in entries:
        cred_dict = {
            "name": entry["title"],
            "login": "",
            "password": entry["secureContents"]["password"],
            "comment": entry["secureContents"].get("notesPlain", "")
        }
        credentials.append(cred_dict)
    return credentials
