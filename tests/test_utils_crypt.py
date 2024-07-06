import os
import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.utils.crypt import get_fernet_key, encrypt_str, decrypt_str


PRIVATE_KEY = 'foobarbaz!1234567890'
os.environ['POTNANNY_SECRET'] = PRIVATE_KEY


class TestCryptUtils(IsolatedAsyncioTestCase):
    async def test_get_key(self):
        key = get_fernet_key()
        assert isinstance(key, bytes)


    async def test_encrypt(self):
        plain = 'foo bar baz'
        secret = encrypt_str(plain)
        assert isinstance(secret, str)
        assert secret.startswith('g')
        assert secret.endswith('=')


    async def test_decrypt(self):
        plain = 'foo bar baz'
        secret = encrypt_str(plain)
        decoded = decrypt_str(secret)
        assert decoded == plain


if __name__ == '__main__':
    unittest.main()
