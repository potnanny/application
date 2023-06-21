import asyncio
import unittest
import datetime
import random
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.models.interface import ObjectInterface
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.controllers.environment import (get_environments,
    get_room_environments)

# globals
CREATED = False
NOW = datetime.datetime.now().replace(second=0, microsecond=0)

class TestEnvironmentCtrl(IsolatedAsyncioTestCase):
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

                start = 0
                for minute in range(0,30,10):
                    dt = NOW - datetime.timedelta(minutes=minute)
                    for t in ['temperature','humidity','vpd', 'battery']:
                        if t == 'temperature':
                            if not start:
                                start = 60
                            v = start + minute
                        else:
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


    async def test_get_environment(self):
        results = await get_environments()
        assert len(results) == 2


    async def test_room_environment(self):
        results = await get_room_environments(2)
        print(results)
        assert len(results) == 3



if __name__ == '__main__':
    unittest.main()
