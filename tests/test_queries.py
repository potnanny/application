import asyncio
import unittest
import datetime
import random
from unittest import IsolatedAsyncioTestCase
from sqlalchemy.sql import text
import potnanny.database as db
from potnanny.models.interface import ObjectInterface, execute_statement
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.controllers.environment import get_environments

CREATED = False
NOW = datetime.datetime.now().replace(second=0, microsecond=0)

class TestQueries(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

        if not CREATED:
            await self.build_models()

    async def build_models(self):
        global CREATED
        CREATED = True

        # add rooms
        for room in [1,2]:
            try:
                opts = {'name': f"Room {room}"}
                r = Room(**opts)
                await r.insert()
            except Exception as x:
                pass

            # add room devices
            for device in [1,2,3]:
                try:
                    opts = {
                        'name': f"Device {device}/{r.id}",
                        'room_id': r.id}
                    d = Device(**opts)
                    await d.insert()
                except Exception as x:
                    pass

                for minute in range(0,30,10):
                    dt = NOW - datetime.timedelta(minutes=minute)
                    for t in ['temperature','humidity','vpd']:
                        v = random.random() * 10
                        opts = {
                            'type': t,
                            'value': v,
                            'device_id': d.id,
                            'created': dt
                        }
                        obj = Measurement(**opts)
                        try:
                            await obj.insert()
                        except Exception as x:
                            pass


    async def asyncTearDown(self):
        pass


    async def test_check_measurements(self):
        stmt = text("""
            SELECT * FROM
                (SELECT id, name FROM rooms) as a
                LEFT JOIN (
                    SELECT
                        d.room_id,
                        m.type,
                        m.value,
                        avg(m.value),
                        max(m.created)
                    FROM
                        measurements as m,
                        devices as d
                    WHERE
                        m.device_id = d.id
                    AND
                        m.type IN ('vpd','temperature', 'humidity')
                    GROUP BY
                        d.room_id,
                        m.type
                ) as b
                ON a.id = b.room_id

        """)
        results = await execute_statement(stmt)
        rows = results.all()
        for r in rows:
            print(r)



if __name__ == '__main__':
    unittest.main()
