import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.control import Control


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Control.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        async with db.connection():
            control = await Control.create(name='control 1',
                outlet=1,
                attributes={'foo': 'bar'},
                device_id=1)
            await control.save()
            assert control.id > 0

    async def test_update(self):
        async with db.connection():
            control = await Control.create(name='control 2',
                outlet=1,
                attributes={'foo': 'bar!'},
                device_id=2)
            await control.save()

            control.attributes = {'foo': 'bar'}
            await control.save()
            assert control.attributes == {'foo': 'bar'}

    async def test_delete(self):
        async with db.connection():
            control = await Control.create(name='control 3',
                outlet=1,
                attributes={'foo': 'bar'},
                device_id=3)
            await control.save()
            pk = control.id
            await control.delete_instance()

            row = await Control.select().where(Control.name == 'control 3')
            assert len(row) == 0


if __name__ == '__main__':
    unittest.main()
