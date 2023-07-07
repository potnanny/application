import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
import potnanny.database as db
from potnanny.plugins.mixins import InterfaceMixin
from potnanny.plugins import ActionPlugin


class DeviceTest(ActionPlugin):
    pass


class TestMixins(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_find(self):
        name = '__main__.DeviceTest'
        klass = InterfaceMixin.class_from_name(name)
        obj = klass()
        assert type(obj) is DeviceTest




if __name__ == '__main__':
    unittest.main()
