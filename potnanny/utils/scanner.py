import asyncio
import logging
from bleak import BleakScanner
from potnanny.locks import LOCKS

logger = logging.getLogger(__name__)


class BLEScanner:

    def __init__(self, *args, **kwargs):
        self.lock = LOCKS['bluetooth']
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def scan_advertised(self, seconds=3, callback=None):
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
                scanner = BleakScanner()
                scanner.register_detection_callback(cb)
                await scanner.start()
                await asyncio.sleep(timeout)
                await scanner.stop()
            except Exception as x:
                logger.warning(x)

        if callback is None:
            callback = default_callback

        if self.lock:
            async with self.lock:
                await callback_scan(callback, seconds)
        else:
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
        if self.lock:
            async with self.lock:
                devices = await BleakScanner.discover()
        else:
            devices = await BleakScanner.discover()

        return devices

