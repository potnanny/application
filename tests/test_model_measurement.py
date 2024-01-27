import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.measurement import Measurement


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Measurement.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        async with db.connection():
            meas = await Measurement.create(
                type='temperature', value=68.0, device_id=1)
            await meas.save()
            assert meas.id > 0

    async def test_update(self):
        async with db.connection():
            meas = await Measurement.create(
                type='humidity', value=55.0, device_id=1)
            await meas.save()

            meas.value = 55
            await meas.save()
            assert meas.value == 55.0

    async def test_delete(self):
        async with db.connection():
            meas = await Measurement.create(
                type='vpd', value=1.0, device_id=1)
            await meas.save()
            pk = meas.id
            await meas.delete_instance()

            row = await Measurement.select().where(Measurement.id == pk)
            assert len(row) == 0


if __name__ == '__main__':
    unittest.main()
