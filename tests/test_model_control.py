import asyncio
import unittest
import potnanny.database as db
from unittest import IsolatedAsyncioTestCase
from potnanny.models.control import Control


class TestDeviceModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)

    async def asyncTearDown(self):
        pass

    async def test_create(self):
        obj = Control(
            name='test',
            device_id=1,
            attributes={
                'input_device_id': 2,
                'type': 'temperature',
                'on': {
                    'condition': 'gt',
                    'threshold': 60
                },
                'off': {
                    'condition': 'lt',
                    'threshold': 50
                }
            }
        )
        await obj.insert()
        assert obj.eval("1 gt 0") is True
        assert obj.eval("0 lt 1") is True
        assert obj.eval("0 ge 0") is True
        assert obj.eval("1 ne 0") is True
        assert obj.eval("1 == 1") is True
        assert obj.eval("1 != 1") is False


if __name__ == '__main__':
    unittest.main()
