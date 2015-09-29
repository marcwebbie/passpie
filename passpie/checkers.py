from copy import deepcopy
from datetime import datetime, timedelta


def repeated(credentials, limit):
    result_credentials = deepcopy(credentials)
    for i, cred in enumerate(credentials):
        rep = [c['fullname'] for c in credentials
               if cred['password'] == c['password'] and
               cred['fullname'] != c['fullname']][:limit]
        if not rep:
            rep = None
        result_credentials[i]['repeated'] = rep
    return result_credentials


def modified(credentials, days):
    result_credentials = deepcopy(credentials)
    for i, cred in enumerate(credentials):
        modified_delta = (datetime.now() - cred["modified"])
        if modified_delta > timedelta(days=days):
            modified_time = "{} days ago".format(modified_delta.days)
        else:
            modified_time = None
        result_credentials[i]['modified'] = modified_time
    return result_credentials
