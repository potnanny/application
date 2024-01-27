import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.device import Device


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Device.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        async with db.connection():
            device = await Device.create(name='device 1',
                interface='foo.bar.baz')
            await device.save()
            assert device.id > 0

    async def test_update(self):
        async with db.connection():
            device = await Device.create(name='device 2',
                interface='foo.bar.baz')
            await device.save()

            device.attributes = {'foo': 'bar'}
            await device.save()
            assert device.attributes == {'foo': 'bar'}

    async def test_delete(self):
        async with db.connection():
            device = await Device.create(name='device 3',
                interface='foo.bar.baz')
            await device.save()
            pk = device.id
            await device.delete_instance()

            row = await Device.select().where(Device.name == 'device 3')
            assert len(row) == 0


if __name__ == '__main__':
    unittest.main()
