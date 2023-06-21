import asyncio
import unittest
import datetime
import json
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models.user import User
from potnanny.models.interface import ObjectInterface


class TestUtilsModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

        try:
            opts = {
                'name': 'test',
                'roles': 'user',
                'password': 'invalid!'
            }
            user = User(**opts)
            await user.insert()
        except:
            pass

    async def asyncTearDown(self):
        pass

    async def test_get_name(self):
        ifc = ObjectInterface(User)
        obj = await ifc.get_by_name('test')
        assert obj is not None
        assert obj.name == 'test'

    async def test_get_id(self):
        ifc = ObjectInterface(User)
        obj = await ifc.get_by_id(2)
        assert obj is not None
        assert obj.name == 'test'

    async def test_get_bad_id(self):
        ifc = ObjectInterface(User)
        obj = await ifc.get_by_id(999)
        assert obj is None

    async def test_get_all(self):
        ifc = ObjectInterface(User)
        objects = await ifc.get_all()
        assert len(objects) > 0

    async def test_delete_user(self):
        opts = {
            'name': 'temporary',
            'roles': 'user',
            'password': 'invalid!'}

        user = User(**opts)
        await user.insert()

        pk = user.id

        results = await ObjectInterface(User).delete(pk)
        assert results is None

        obj = await ObjectInterface(User).get_by_id(pk)
        assert obj is None


if __name__ == '__main__':
    unittest.main()
