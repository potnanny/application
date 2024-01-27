import unittest
import peewee
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.keychain import Keychain


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Keychain.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        async with db.connection():
            kc = await Keychain.create(name='settings',
                attributes={'temperature_display': 'F'})
            await kc.save()
            assert kc.id > 0

    async def test_update(self):
        async with db.connection():
            kc = await Keychain.create(name='foo',
                attributes={'bar': 13, 'baz': 42})
            await kc.save()

            kc.attributes.update({'baz': 43})
            await kc.save()
            assert kc.attributes == {'bar': 13, 'baz': 43}

    async def test_delete(self):
        async with db.connection():
            kc = await Keychain.create(name='bar',
                attributes={'one': 1})
            await kc.save()
            pk = kc.id
            await kc.delete_instance()

            row = await Keychain.select().where(Keychain.id == pk)
            assert len(row) == 0

    async def test_unique_name(self):
        with self.assertRaises(peewee.IntegrityError):
            async with db.connection():
                kc1 = await Keychain.create(name='user',
                    attributes={'name': 'foo'})
                await kc1.save()

                kc2 = await Keychain.create(name='user',
                    attributes={'name': 'foo'})
                await kc2.save()


if __name__ == '__main__':
    unittest.main()
