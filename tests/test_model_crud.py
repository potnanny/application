import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.interface import ObjectInterface



class TestMixins(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)


    async def asyncTearDown(self):
        pass


    async def test_crud_delete(self):
        room = Room(name='test room')
        await room.insert()
        assert room.id > 0

        # test that room was created in db
        ifc = ObjectInterface(Room)
        rooms = await ifc.get_all()
        assert len(rooms) == 1

        # test that the room was deleted from db
        await room.delete()
        rooms = await ifc.get_all()
        assert len(rooms) == 0


    async def test_crud_update(self):
        room = Room(name='room with notes', notes='my test')
        await room.insert()
        assert room.id > 0

        room.notes += " more test"
        await room.update()

        # ensure the update is reflected in the database
        ifc = ObjectInterface(Room)
        obj = await ifc.get_by_name('room with notes')
        assert obj.notes == 'my test more test'


    async def test_crud_dict_update(self):
        device = Device(
            name='test device',
            interface='mytest.foo.bar.Baz',
            attributes={'foo': 'bar'})
        await device.insert()
        assert device.id > 0

        device.attributes['baz'] = 13
        await device.update()

        # ensure the update is reflected in the database
        ifc = ObjectInterface(Device)
        obj = await ifc.get_by_name('test device')
        assert obj.attributes == {'foo': 'bar', 'baz': 13}

if __name__ == '__main__':
    unittest.main()
