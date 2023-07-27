import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.models.interface import ObjectInterface
from potnanny.models.user import User


class TestUserModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass


    async def test_create(self):
        opts = {
            'name': 'testuser',
            'password': 'qwerty123456',
            'roles': 'user',
        }
        user = User(**opts)

        await user.insert()
        assert user.id > 0
        assert user.name == 'testuser'


    async def test_get_id(self):
        user = await ObjectInterface(User).get_by_id(1)
        assert user is not None


    async def test_get_name(self):
        user = await ObjectInterface(User).get_by_name('admin')
        assert user is not None


    async def test_update(self):
        opts = {
            'name': 'testuser2',
            'password': 'qwerty123456',
            'roles': 'user',
        }
        user = User(**opts)
        await user.insert()

        user.name = 'modified'
        await user.update()
        assert user.name == 'modified'


    async def test_delete(self):
        opts = {
            'name': 'testuser3',
            'password': 'qwerty123456',
            'roles': 'user',
        }
        user = User(**opts)
        await user.insert()
        assert user.id > 0

        pk = user.id
        await user.delete()

        obj = await ObjectInterface(User).get_by_id(pk)
        assert obj is None


if __name__ == '__main__':
    unittest.main()
