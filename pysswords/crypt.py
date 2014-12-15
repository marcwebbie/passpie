# import os
# from shutil import which
# import gnupg


# class GPG(object):
#     def __init__(self, database_path, binary="gpg2"):
#         self.gnupg_path = os.path.join(database_path, ".gnupg")
#         self._gpg = gnupg.GPG(which(binary), homedir=self.gnupg_path)

#     def default_key(self):
#         self._gpg.list_keys()[0]
