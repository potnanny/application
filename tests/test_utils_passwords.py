import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.user import User
from potnanny.utils.password import verify_password, hash_password


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await User.create_table()


class TestUtils(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass

    async def test_hashing(self):
        pw = hash_password('foobar!')
        print(pw)
        assert pw

    async def test_verify(self):
        pw = hash_password('foobar!')
        assert verify_password('foobar!', pw) is True
        assert verify_password('foobar!', 'foobar') is False

if __name__ == '__main__':
    unittest.main()
