import asyncio
import unittest
import datetime
import json
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models import Room
from potnanny.models.utils import (get_class_objects, update_class_object,
    delete_class_object)


class TestUtilsModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        for i in (1,2,3):
            r = Room(name='test room %d' % i)
            await r.insert()

        results = await get_class_objects(Room)
        assert len(results) == 3

        room = await get_class_objects(Room, 1)
        assert type(room) is Room

        missing = await get_class_objects(Room, 99)
        assert missing is None

if __name__ == '__main__':
    unittest.main()
