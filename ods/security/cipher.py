import base64
import os

import flask
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AESCipher(object):
    """Encrypt and decrypt data using AES-256 encryption in CBC mode. This
    requires a 256-bit (32-byte) key for operation.
    """
    block_size = algorithms.AES.block_size / 8

    def __init__(self, key=None):
        """Instantiate a cipher object with a given encryption key. If a key has
        not been passed during instantiation, the encryption key is read from
        the current Flask app's config file using the ``DATABASE_KEY`` key.

        :attr block_size: AES block size.

        :param str key: A 256 bit (32 byte) encryption key

        :raises ValueError: Key is not of the correct length.
        """
        if key:
            self._key = key
        else:
            try:
                self._key = flask.current_app.config['DATABASE_KEY']
            except RuntimeError as err:
                # This doesn't always work for what I'm trying to catch
                # Rethink this try block
                flask.current_app.logger.exception(err)
                flask.current_app.logger.error('Unable to load DATABASE_KEY '
                                               'from the application config.')

        if len(self._key) * 8 != 256:
            raise ValueError('Invalid key size (must be 256 bit)')

    def _cipher(self, iv):
        """Returns a ``cryptography.hazmat.primitives.ciphers.Cipher`` object
        to the :meth:`encrypt` and :meth:`decrypt` methods.

        The ``iv`` parameter MUST be a secure, randomized value whose length
        matches the :attr:`block_size` when it is created as a part of
        encrypting new data. The ``iv`` will be extracted from encrypted data by
        :meth:`decrypt` and passed to this function.

        :param iv: Initialization vector (**Only** provide secure, random data
            to this parameter when creating new ciphers!).

        :raises ValueError: IV does not match :attr:`block_size`.

        :returns: Cipher using AES algorithm.
        :rtype: cryptography.hazmat.primitives.ciphers.Cipher
        """
        if len(iv) != AESCipher.block_size:
            raise ValueError('Invalid IV size (must be 128 bit)')

        return Cipher(
            algorithms.AES(self._key),
            modes.CBC(iv),
            backend=default_backend()
        )

    def encrypt(self, raw):
        """Encrypts data and returns it as a base 64 string.

        :param raw: Raw data.

        :returns: An encrypted base 64 encoded string.
        :rtype: str
        """
        iv = os.urandom(AESCipher.block_size)
        encryptor = self._cipher(iv).encryptor()
        padded = self._pad(str(raw))
        cipher_text = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(cipher_text + iv)

    def decrypt(self, encoded):
        """Accepts an encrypted base 64 string and returns the decrypted data in
        its original state. The ``cipher text`` and ``iv`` are extracted from
        the data after it is decoded from its base 64 string.

        The ``iv`` is expected to be at the end of this data and the ``cipher
        text`` in front of it. The position is determined the by
        :attr:`block_size` which the ``iv`` is expected to match.

        After decryption the result is un-padded before being returned.

        If the decryption fails an empty string is returned. This could be due
        to an incorrect encryption ``key`` or an incorrect ``iv``.

        :param encoded: An encrypted base 64 string.

        :returns: Raw decrypted data.
        """
        raw = base64.b64decode(encoded)
        cipher_text = raw[:-AESCipher.block_size]
        iv = raw[-AESCipher.block_size:]
        decryptor = self._cipher(iv).decryptor()
        padded = decryptor.update(cipher_text) + decryptor.finalize()
        return self._unpad(padded)

    @staticmethod
    def _pad(raw):
        """Adds padding to raw data to make its length a multiple of the
        :attr:`block_size`.

        First, the remainder from a modulus of the ``raw`` content length and
        the ``block_size`` is obtained. Then, this is subtracted from the
        ``block_size`` to produce an integer from ``1`` to the `block_size`.
        This is the ``ordinal``.

        The ``ordinal`` is used to determine the padding character using
        :func:`chr`. That character is multiplied by the ``ordinal`` and the
        resulting pad string is appended to the end of the ``raw`` data.

        :param raw: Raw data.

        :returns: Padded raw data.
        """
        ordinal = AESCipher.block_size - len(raw) % AESCipher.block_size
        return raw + ordinal * chr(ordinal)

    @staticmethod
    def _unpad(padded):
        """Removes padding from padded data.

        The padding is removed using a slice. The amount removed is determined
        by the ``ordinal`` number of the last character of the padded data.

        :param padded: Padded raw data.
        :return: Un-padded raw data.
        """
        return padded[:-ord(padded[len(padded) - 1:])]
