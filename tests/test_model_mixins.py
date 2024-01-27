import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.device import Device
from potnanny.plugins.utils import load_plugins


async def init_tables():
    db.init('aiosqlite:////tmp/test.db')
    async with db.connection():
        await Device.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        print("loading plugins...")
        load_plugins('~/potnanny/plugins')
        await init_tables()

    async def asyncTearDown(self):
        pass

    async def test_setup(self):
        opts = {
            'name': 'SwitchBot Hygrometer',
            'interface': 'device.ble.switchbot_hygrometer.SwitchbotHygrometer',
            'attribute': {"address": "EB:B3:0E:C7:7C:D2"}
        }

        d = await Device.create(**opts)
        await d.save()
        print("device saved")

        print("device plugin details...")
        print(d.plugin)


if __name__ == '__main__':
    unittest.main()
