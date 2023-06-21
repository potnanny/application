import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.models.interface import ObjectInterface
from potnanny.models.keychain import Keychain


class TestKeychainModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        opts = {
            'name': 'mail-auth',
            'attributes': {
                'user': 'test@gmail.com',
                'auth_token': '1234567890',
                'refresh_token': '1234567890',
            }
        }
        obj = Keychain(**opts)

        await obj.insert()
        assert obj.id >= 0
        assert 'user' in obj.attributes
        assert obj.attributes['user'] == 'test@gmail.com'


    async def test_get_id(self):
        obj = await ObjectInterface(Keychain).get_by_id(1)
        assert obj is not None


    async def test_get_name(self):
        obj = await ObjectInterface(Keychain).get_by_name('settings')
        assert obj is not None


    async def test_update(self):
        opts = {
            'name': 'mail-auth2',
            'attributes': {
                'user': 'test@gmail.com',
                'auth_token': '1234567890',
                'refresh_token': '1234567890',
            }
        }
        obj = Keychain(**opts)
        await obj.insert()

        obj.attributes['user'] = 'modified@gmail.com'
        await obj.update()
        assert obj.attributes['user'] == 'modified@gmail.com'


    async def test_delete(self):
        opts = {
            'name': 'mail-auth3',
            'attributes': {
                'user': 'test@gmail.com',
                'auth_token': '1234567890',
                'refresh_token': '1234567890',
            }
        }
        obj = Keychain(**opts)
        await obj.insert()
        assert obj.id > 0

        pk = obj.id
        await obj.delete()

        check = await ObjectInterface(Keychain).get_by_id(pk)
        assert check is None


if __name__ == '__main__':
    unittest.main()
