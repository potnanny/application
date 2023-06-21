import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
from potnanny.utils.scanner import BLEScanner


class TestBleInterface(IsolatedAsyncioTestCase):
# ###############################################

    async def test_scan_devices(self):
        obj = BLEScanner()
        devices = await obj.scan_devices()
        assert devices

    async def test_scan_advertised(self):
        obj = BLEScanner()
        results = await obj.scan_advertised()
        assert results


if __name__ == '__main__':
    unittest.main()
