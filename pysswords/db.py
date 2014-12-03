import base64
import functools
import json
import sys

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random


BAD_HMAC = 1
BAD_ARGS = 2

def _make_keys(password, salt=None, iterations=100000):
    """Generates two 128-bit keys from the given password using
       PBKDF2-SHA256.
       We use PBKDF2-SHA256 because we want the native output of PBKDF2 to be
       256 bits. If we stayed at the default of PBKDF2-SHA1, then the entire
       algorithm would run twice, which is slow for normal users, but doesn't
       slow things down for attackers.
       password - The password.
       salt - The salt to use. If not given, a new 8-byte salt will be generated.
       iterations - The number of iterations of PBKDF2 (default=100000).

       returns (k1, k2, salt, interations)
    """
    if salt is None:
        # Generate a random 8-byte salt
        salt = Random.new().read(8)

    # Generate a 32-byte (256-bit) key from the password
    prf = lambda p,s: HMAC.new(p, s, SHA256).digest()
    key = PBKDF2(password, salt, 32, iterations)

    # Split the key into two 16-byte (128-bit) keys
    return key[:16], key[16:], salt, iterations

def _make_hmac(message, key):
    """Creates an HMAC from the given message, using the given key. Uses
       HMAC-MD5.
       message - The message to create an HMAC of.
       key - The key to use for the HMAC (at least 16 bytes).

       returns A hex string of the HMAC.
    """
    h = HMAC.new(key)
    h.update(message)
    return h.hexdigest()

def _encrypt(message, key):
    """Encrypts a given message with the given key, using AES-CFB.
       message - The message to encrypt (byte string).
       key - The AES key (16 bytes).

       returns (ciphertext, iv). Both values are byte strings.
    """
    # The IV should always be random
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = cipher.encrypt(message)
    return (ciphertext, iv)

def create(db_path, password, salt=None, iterations=100000):
    # create default file
    with open(db_path, "w") as default_file:
        default_file.write(json.dumps([{}]))

    with open(db_path, "rb") as f:
        file_contents = f.read()

    aes_key, hmac_key, salt, iterations = _make_keys(
        password=password,
        salt=salt,
        iterations=iterations
    )
    ciphertext, iv = _encrypt(file_contents, aes_key)
    hmac = _make_hmac(ciphertext, hmac_key)

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
