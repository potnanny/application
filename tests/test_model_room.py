import asyncio
import unittest
import datetime
import json
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models import Room, Device
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class TestRoomModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        r = Room(
            name='test room 1',
            notes='test')
        await r.insert()
        assert r.id >= 0

    async def test_relationships(self):
        r = Room(name='test room 2')
        await r.insert()

        i = Device(
            name='test input 2',
            notes='test',
            interface='plugins.input.ble.test.TestInput',
            attributes={'address': '11:22:33:44:55:66'},
            room_id=r.id)
        await i.insert()

        # each of the above insert()s was performed in a different session.
        # so, we must re-query the room, to get all objects together in one
        # session...
        room = None
        async with db.session() as session:
            stmt = select(Room).filter(
                Room.name == 'test room 2').options(
                selectinload(Room.devices)
            )

            results = await session.execute(stmt)
            room = results.scalar()

        assert('devices' in room.as_dict())
        assert(type(room.as_dict()['devices']) is list)

if __name__ == '__main__':
    unittest.main()
