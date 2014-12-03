import base64
import json

from pysswords import crypt


class Database(object):
    """Represents json encrypted files on the database"""

    DEFAULT_CONTENT = '[{}]'

    @staticmethod
    def create(db_path, password, salt=None, iterations=100000):
        """Create a new db file pointing to `db_path`
        encrypted with `passwords`.
        `salt` is the salt used. If none it generates a 8-byte salt.
        `iterations` is the number of iterations of PBKDF2
        """
        # create default file
        with open(db_path, "w") as default_file:
            default_file.write(json.dumps([{}]))

        with open(db_path, "rb") as f:
            file_contents = f.read()

        aes_key, hmac_key, salt, iterations = crypt.make_keys(
            password=password,
            salt=salt,
            iterations=iterations
        )
        ciphertext, iv = crypt.encrypt(file_contents, aes_key)
        hmac = crypt.make_hmac(ciphertext, hmac_key)

        output = {
            "hmac": hmac,
            "iterations": iterations
        }
        for key, value in ("ciphertext", ciphertext), ("iv", iv), ("salt", salt):
            output[key] = base64.b64encode(value).decode("utf-8")
            output_data = json.dumps(output).encode("utf-8")

        with open(db_path, "wb") as f:
            f.write(output_data)

        return db_path
