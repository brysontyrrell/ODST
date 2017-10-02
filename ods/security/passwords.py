import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey


def _get_key_derivation_function(salt):
    backend = default_backend()
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )


def derive_key(raw):
    salt = os.urandom(16)
    kdf = _get_key_derivation_function(salt)
    return base64.b64encode(kdf.derive(bytes(raw)) + salt)


def verify_key(raw, encoded_key):
    decoded_key = base64.b64decode(encoded_key)
    key = decoded_key[:-16]
    salt = decoded_key[-16:]
    kdf = _get_key_derivation_function(salt)
    try:
        kdf.verify(bytes(raw), key)
    except InvalidKey:
        return False
    else:
        return True

# # Scrypt Method (Requires OpenSSL 1.1.0+)
#
# from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
#
#
# def _get_key_derivation_function(salt):
#     backend = default_backend()
#     return Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=backend)
#
#
# def derive_key(raw):
#     salt = os.urandom(16)
#     kdf = _get_key_derivation_function(salt)
#     return base64.b64encode(kdf.derive(bytes(raw)) + salt)
#
#
# def verify_key(raw, encoded_key):
#     decoded_key = base64.b64decode(encoded_key)
#     key = decoded_key[:-16]
#     salt = decoded_key[-16:]
#     kdf = _get_key_derivation_function(salt)
#     try:
#         kdf.verify(bytes(raw), key)
#     except InvalidKey:
#         return False
#     else:
#         return True
