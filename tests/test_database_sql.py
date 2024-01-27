import unittest
import datetime
import random
from unittest import IsolatedAsyncioTestCase
from peewee import fn
from potnanny.database import db, init_db
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.utils import utcnow


async def init_tables():
    db.init('aiosqlite:////tmp/test.db', pragmas=(('foreign_keys', 1),))

    db.register(Room)
    db.register(Device)
    db.register(Measurement)

    async with db.connection():
        await Room.create_table()
        await Device.create_table()
        await Measurement.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_sql_query(self):
        async with db.connection():
            for i in range(1,11):
                r = await Room.create(name=f"test room {i}")
                await r.save()

        async with db.connection():
            sql = "select * from room"
            results = await db.fetchall(sql)
            assert len(results) >= 10


    async def test_func_query(self):
        now = utcnow()
        async with db.connection():
            r = await Room.create(name='initial room')
            await r.save()

            d = await Device.create(name='initial device', room_id=r.id,
                interface='foo.bar.baz')
            await d.save()

            for i in range(0, 10):
                then = now - datetime.timedelta(minutes=i)
                opts = {
                    'type': 'temperature',
                    'value': random.randrange(65, 80) * 1.0,
                    'device_id': 1,
                    'created': then
                }
                m = await Measurement.create(**opts)
                await m.save()


        async with db.connection():
            query = await Measurement.select(
                Measurement.id,
                Measurement.value,
                Measurement.type,
                Measurement.device_id,
                fn.MAX(Measurement.created)
            ).where(
                Measurement.device_id == 1,
                Measurement.type == "temperature"
            ).group_by(
                Measurement.device_id
            )
            
            m = query[0]
            assert m.created == now



if __name__ == '__main__':
    unittest.main()
