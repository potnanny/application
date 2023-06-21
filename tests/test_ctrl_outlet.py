import asyncio
import unittest
import datetime
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.models.measurement import Measurement
from potnanny.controllers.outlet import OutletControl


class TestOutletCtrl(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

        now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        for outlet in [1, 2]:
            for i in range(1,10):
                then = now - datetime.timedelta(minutes=i)
                opts = {
                    'device_id': 1,
                    'type': f"outlet_{outlet}",
                    'value': outlet - 1,
                    'created': then
                }
                m = Measurement(**opts)
                await m.insert()

    async def asyncTearDown(self):
        pass

    async def test_check_outlet1(self):
        ctl = OutletControl(1, 1)
        state1 = await ctl.last_state(90)
        assert state1 == 0

        state2 = await ctl.last_state(20)
        assert state2 == -1


    async def test_check_outlet2(self):
        ctl = OutletControl(1, 2)
        state1 = await ctl.last_state(90)
        assert state1 == 1

        state2 = await ctl.last_state(20)
        assert state2 == -1


if __name__ == '__main__':
    unittest.main()
