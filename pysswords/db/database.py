import base64
import json

from pysswords import crypt
from .credential import Credential

class Database(object):
    """Represents json encrypted files on the database"""

    DEFAULT_CONTENT = '[]'

    def __init__(self, path, crypt_options, credentials=None):
        self.path = path
        self.crypt_options = crypt_options
        if credentials == None:
            decrypted_credentials = Database.decrypt_credentials(
                path=path,
                password=crypt_options.password
            )
            self.credentials = decrypted_credentials

    @classmethod
    def create(cls, path, crypt_options):
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
            crypt_options=crypt_options
        )
        return database

    @classmethod
    def verify(cls, database_path, password):
        with open(database_path, "rb") as f:
            file_contents = f.read()

        data = json.loads(file_contents.decode("utf-8"))
        ciphertext = base64.b64decode(data["ciphertext"].encode("ascii"))
        iterations = data["iterations"]
        salt = base64.b64decode(data["salt"].encode("ascii"))

        _, hmac_key, _, _ = crypt.make_keys(password, salt, iterations)
        hmac = crypt.make_hmac(ciphertext, hmac_key)
        if hmac != data["hmac"]:
            # TODO: logging
            return False
        else:
            return True

    @classmethod
    def decrypt_credentials(cls, path, password):
        with open(path, "rb") as f:
            file_contents = f.read()

        data = json.loads(file_contents.decode("utf-8"))
        ciphertext = base64.b64decode(data["ciphertext"])
        iv = base64.b64decode(data["iv"])
        iterations = data["iterations"]
        salt = base64.b64decode(data["salt"])

        aes_key, hmac_key, _, _ = crypt.make_keys(password, salt, iterations)
        output_data = crypt.decrypt(ciphertext, aes_key, iv)

        decrypted_credentials = [
            Credential(**c) for c in json.loads(output_data.decode('utf-8'))]

        return decrypted_credentials

    def add_credential(self, credential):
        self.credentials.append(credential)

    def delete_credential(self, **kwargs):
        creds = [c for c in self.credentials
                 if not {k: vars(c)[k] for k in vars(c).keys()
                         if k in kwargs.keys()} == kwargs]
        self.credentials = creds

    def find_credentials(self, **kwargs):
        return [c for c in self.credentials
                if {k: vars(c)[k] for k in vars(c).keys()
                    if k in kwargs.keys()} == kwargs]

    def save(self):
        credentials_json = json.dumps([vars(c) for c in self.credentials])

        aes_key, hmac_key, salt, iterations = crypt.make_keys(
            password=self.crypt_options.password,
            iterations=self.crypt_options.iterations
        )
        ciphertext, iv = crypt.encrypt(credentials_json, aes_key)
        hmac = crypt.make_hmac(ciphertext, hmac_key)

        output = {
            "hmac": hmac,
            "iterations": iterations
        }
        for key, value in ("ciphertext", ciphertext), ("iv", iv), ("salt", salt):
            output[key] = base64.b64encode(value).decode("utf-8")

        with open(self.path, "wb") as f:
            output_data = json.dumps(output).encode("utf-8")
            f.write(output_data)

        return self
