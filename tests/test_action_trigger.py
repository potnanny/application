import os
import unittest
import datetime
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.room import Room
from potnanny.models.action import Action, ActionSchema, ActionTrigger
from potnanny.plugins.base import ActionPlugin

CLEANUP = True
DBFILE = '/tmp/test_action.db'

class MyActionPlugin(ActionPlugin):
    def __init__(self):
        pass

    async def input(self, data):
        for k,v in data.items():
            print(f"data | {k}: {v}")


async def init_tables():
    try:
        db.init(f'aiosqlite:///{DBFILE}', pragmas=(('foreign_keys', 1),))
        db.register(Room)
        db.register(Action)
        db.register(ActionTrigger)
        await Room.create_table()
        await Action.create_table()
        await ActionTrigger.create_table()

        r = await Room.create(
            name='test room')
        await r.save()

        d = await Device.create(
            name='test device',
            interface='foo.bar.Baz',
            room_id=r.id)
        await d.save()
    except:
        pass


class TestModels(IsolatedAsyncioTestCase):
    @classmethod
    def tearDownClass(cls):
        if CLEANUP:
            try:
                os.unlink(DBFILE)
            except:
                pass

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        obj = await Action.create(
            name='test action',
            room_id=1,
            interface='__main__.MyActionPlugin',
            attributes={
                'condition': '>=',
                'threshold': 90
            }
        )
        await obj.save()

        m = {
            'device_id': 1,
            'value': 99.0,
            'type': 'temperature'}

        await obj.input(m)


if __name__ == '__main__':
    unittest.main()
