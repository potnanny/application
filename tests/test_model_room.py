import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.room import Room, RoomSchema


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Room.create_table()


class TestSchemas(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass

    async def test_basic_schema(self):
        jsondata = {'name': 'test room', 'foo': 'bar'}
        schema = RoomSchema()
        data = schema.load(jsondata)
        assert data is not None
        assert 'foo' not in data


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        async with db.connection():
            room = await Room.create(name='room 1')
            await room.save()
            assert room.id > 0

        assert isinstance(room.as_dict(), dict)


    async def test_update(self):
        async with db.connection():
            room = await Room.create(name='room 2')
            await room.save()

            room.notes = 'test notes'
            await room.save()
            assert room.notes == 'test notes'

        assert isinstance(room.as_dict(), dict)


    async def test_delete(self):
        async with db.connection():
            room = await Room.create(name='room 3')
            await room.save()
            pk = room.id
            await room.delete_instance()

            row = await Room.select().where(Room.name == 'room 3')
            assert len(row) == 0


if __name__ == '__main__':
    unittest.main()
