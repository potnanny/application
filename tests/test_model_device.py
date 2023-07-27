import asyncio
import unittest
import random
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.models.interface import ObjectInterface
from potnanny.plugins.base import BluetoothDevicePlugin


class MyClass(BluetoothDevicePlugin):
    name = "test"
    description = "testing desc"
    reports = ['temperature', 'humidity']

    def __init__(self, *args, **kwargs):
        pass


class TestDeviceModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        obj = Device(
            interface='__main__.MyClass',
            attributes={'address': '11:22:33:44:55:66'},
            name='11-22-33-44-55-66',
        )

        await obj.insert()
        assert obj.id >= 0
        assert obj.attributes['address'] == '11:22:33:44:55:66'
        assert 'vpd' in obj.as_dict()['reports']


if __name__ == '__main__':
    unittest.main()
