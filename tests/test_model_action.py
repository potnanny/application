import os
import unittest
import datetime
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.room import Room
from potnanny.models.action import Action, ActionSchema, ActionTrigger

CLEANUP = True
DBFILE = '/tmp/test.db'

async def init_tables():
    try:
        db.init(f'aiosqlite:///{DBFILE}', pragmas=(('foreign_keys', 1),))
        db.register(Room)
        db.register(Action)
        db.register(ActionTrigger)
        await Room.create_table()
        await Action.create_table()
        await ActionTrigger.create_table()
        r = await Room.create(name='test room')
        await r.save()
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
        async with db.connection():
            obj = await Action.create(
                name='test action',
                room_id=1,
                interface='foo.bar.Baz',
                attributes={
                    'threshold': 'value gt 90'
                }
            )
            await obj.save()

        assert obj.id > 0
        assert isinstance(obj.as_dict(), dict)


    async def test_open_trigger(self):
        tag = 'test open trigger'

        a1 = await Action.create(
            name=f'action 1 ({tag})',
            room_id=1,
            interface='foo.bar.Baz1',
            attributes={
                'threshold': 'value gt 90'
            }
        )
        await a1.save()

        a2 = await Action.create(
            name=f'action 2 ({tag})',
            room_id=1,
            interface='foo.bar.Baz2',
            attributes={
                'threshold': 'value gt 90',
                'sleep_minutes': 1
            }
        )
        await a2.save()

        # create trigger assigned to action 2
        await a2.init_trigger()

        # check there IS NOT an open trigger
        truth1 = await a1.has_open_trigger()
        assert truth1 is False

        # check there IS an open trigger
        truth2 = await a2.has_open_trigger()
        assert truth2 is True




if __name__ == '__main__':
    unittest.main()
