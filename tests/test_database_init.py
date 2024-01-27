import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db, init_db
from potnanny.models.room import Room
from potnanny.models.device import Device


async def init_tables():
    await init_db(
        'aiosqlite:////tmp/db.db',
        pragmas=(('foreign_keys', 1),)
    )


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_foreignkey_cascade(self):
        async with db.connection():
            # create a parent
            room = await Room.create(name='room 1')
            await room.save()
            assert room.id > 0
            pk = room.id

            # create a child
            device = await Device.create(
                name='device 1', interface='foo.bar.baz', room_id=pk)
            await device.save()
            assert device.id > 0

            # delete the parent
            await room.delete_instance()

            # child should not exist
            results = await Device.select().where(Device.room_id == pk)
            assert len(results) == 0

if __name__ == '__main__':
    unittest.main()
