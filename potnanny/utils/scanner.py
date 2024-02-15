import asyncio
import logging
from bleak import BleakScanner
from potnanny.ble import lock


logger = logging.getLogger(__name__)


class BLEScanner:

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def scan_advertised(self, seconds=5, callback=None):
        """
        scan for BLE device advertisement data

        args:
            - seconds (int)
            - discovery callback function (optional)
        returns:
            - list
        """

        discovered = []

        def default_callback(reporting, advertisement):
            nonlocal discovered
            discovered.append((reporting, advertisement))

        async def callback_scan(cb, timeout=1):
            try:
                async with BleakScanner(cb) as scanner:
                    await asyncio.sleep(timeout)
            except Exception as x:
                logger.warning(x)

        if callback is None:
            callback = default_callback

        async with lock:
            await callback_scan(callback, seconds)

        return discovered


    async def scan_advertised_filter(self, addresses, seconds=3, callback=None):
        """
        Returns list of advertised data, only for devices matching a list of
        MAC addresses
        """

        filtered = []
        results = await self.scan_advertised(seconds, callback)
        if not addresses:
            return results

        for d in results:
            if d[0].address in addresses:
                filtered.append(d)

        return filtered


    async def scan_devices(self):
        """
        Scan only for devices reporting
        """

        devices = None

        async with lock:
            devices = await BleakScanner.discover()

        return devices
