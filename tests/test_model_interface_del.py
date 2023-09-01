import asyncio
import unittest
import datetime
import json
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.interface import ObjectInterface


class TestUtilsModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_cascade_delete(self):
        # create a room
        room = Room(name='test room')
        await room.insert()

        # add a device to the room
        device = Device(
            name='test device',
            interface='potnanny.bogus.test',
            room_id=room.id)
        await device.insert()

        # delete the room with the obj interface
        ifc = ObjectInterface(Room)
        result = await ifc.delete(room.id)
        print("room deleted")

        # ensure rooms devices were also deleted
        ifc = ObjectInterface(Device)
        devices = await ifc.get_all()
        assert len(devices) == 0


if __name__ == '__main__':
    unittest.main()
