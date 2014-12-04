import base64
import json

from pysswords import crypt


class Database(object):
    """Represents json encrypted files on the database"""

    DEFAULT_CONTENT = '[{}]'

    def __init__(self, path, credentials, crypt_options):
        self.path = path
        self.credentials = credentials
        self.crypt_options = crypt_options

    @staticmethod
    def create(path, crypt_options):
        """Create a new empty Database at `path`
        `crypt_options` is an instance of pysswords.crypt.CryptOptions

        returns a Database instance
        """

        content = Database.DEFAULT_CONTENT

        aes_key, hmac_key, salt, iterations = crypt.make_keys(
            password=crypt_options.password,
            salt=crypt_options.salt,
            iterations=crypt_options.iterations
        )
        ciphertext, iv = crypt.encrypt(content, aes_key)
        hmac = crypt.make_hmac(ciphertext, hmac_key)

        output = {
            "hmac": hmac,
            "iterations": crypt_options.iterations
        }

        for key, value in (("ciphertext", ciphertext),
                           ("iv", iv),
                           ("salt", salt)):
            output[key] = base64.b64encode(value).decode("utf-8")
            output_data = json.dumps(output).encode("utf-8")

        with open(path, "wb") as f:
            f.write(output_data)

        database = Database(
            path=path,
            credentials=[],  # empty credentials
            crypt_options=crypt_options
        )
        return database

    def add_credential(self, credential):
        self.credentials.append(credential)

    def delete_credential(self, **kwargs):
        creds = [c for c in self.credentials
                 if not {k: vars(c)[k] for k in vars(c).keys() if k in kwargs.keys()} == kwargs]
        self.credentials = creds
