import asyncio
import unittest
import potnanny.database as db
from potnanny.locks import init_locks
from unittest import IsolatedAsyncioTestCase
from potnanny.models import Measurement, Device


class TestMeasurementModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)
        await init_locks()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        m = Measurement(
            device_id=1,
            type='temperature',
            value=74.2
        )
        await m.insert()
        assert m.id >= 0
        assert type(m.as_dict()) is dict
        assert m.value == 74.2

if __name__ == '__main__':
    unittest.main()
