import os
import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.room import Room

DBFILE = '/tmp/test.db'

async def init_tables():
    db.init(f'aiosqlite:///{DBFILE}', pragmas=(('foreign_keys', 1),))
    db.register(Room)
    await Room.create_table()
    async with db.transaction():
        r = await Room.get_or_create(name='test')

class TestDBFuncs(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(DBFILE)
        except:
            pass

    async def test_transaction_rollback(self):
        async with db.transaction() as trx:
            for i in [1,2,3,4]:
                r = await Room.create(name=f"room {i}")

            await trx.rollback()

        check = await Room.select().where(Room.name == "room 1").first()
        assert check is None


    async def test_transaction(self):
        async with db.transaction() as trx:
            for i in [10,11,12,13]:
                r = await Room.create(name=f"room {i}")

        check = await Room.select().where(Room.name == "room 10").first()
        assert check.name == 'room 10'


if __name__ == '__main__':
    unittest.main()
