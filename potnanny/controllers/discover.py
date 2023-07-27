import re
import asyncio
import logging
import potnanny.database as db
from potnanny.models.interface import ObjectInterface
from potnanny.plugins.base import BluetoothDevicePlugin
from potnanny.models.device import Device
from potnanny.utils.scanner import BLEScanner
from potnanny.locks import LOCKS

logger = logging.getLogger(__name__)


class DiscoveryClient:
    def __init__(self, *args, **kwargs):
        self.scanner = BLEScanner()


    async def discover(self):
        results = []
        existing = await ObjectInterface(Device).get_all()
        found = await self.scanner.scan_devices()
        devices = self.recognized_devices([f for f in found])
        for entry in devices:
            device, interface, attrs = entry
            if self.is_existing_device(existing, device, interface):
                continue

            opts = {
                'name': device.name,
                'interface': interface,
                'attributes': {'address': device.address},
                'room_id': None }

            # manufacturer bluetooth advertised names are often stupid, and
            # meaningless to the end user.
            # here, we replace it with the plugin name attribute to be more
            # helpful.
            try:
                klass = BluetoothDevicePlugin.get_named_class(opts['interface'])
                if klass:
                    opts['name'] = klass.name
            except:
                pass

            try:
                opts['attributes'].update(attrs)
            except:
                pass

            results.append(opts)

        for d in results:
            try:
                obj = Device(**d)
                await obj.insert()
            except Exception as x:
                logger.warning(x)

        return results


    async def insert_devices(self, devices):
        async def db_execute(f):
            """execute the session function"""

            if 'db' in LOCKS and LOCKS['db'] is not None:
                async with LOCKS['db']:
                    await f()
            else:
                await f()

        async def perform():
            try:
                async with db.session() as session:
                    for d in devices:
                        obj = Device(**d)
                        session.add(obj)

                    await session.commit()
            except Exception as x:
                logger.warning(x)

        await db_execute(perform)


    def recognized_devices(self, devices):
        """
        Return a filtered list of ble devices that we can communicate with.
        [(device, interface_name), ]
        """

        results = []
        for d in devices:
            fingerprint = {'address': d.address, 'name': d.name}
            for p in BluetoothDevicePlugin.plugins:
                attrs = None
                try:
                    if p.recognize_this(fingerprint):
                        found = '.'.join((p.__module__, p.__name__))
                        try:
                            attrs = p.attributes
                        except:
                            pass
                        results.append((d, found, attrs))
                except:
                    continue

        return results


    def is_existing_device(self, existing, device, interface):
        """
        Compare ble-device to list of existing devices, and see if match
        exists already

        args:
            - list of existing devices
            - device to inspect
            - plugin interface
        returns:
            - bool
        """

        def match_exists(e, plugin, address):
            try:
                if e.interface != plugin:
                    return False

                a1 = address.upper()
                a2 = e.attributes['address'].upper()
                if a1 == a2:
                    return True
            except Exception as x:
                logger.warning(str(x))

            return False

        for e in existing:
            if match_exists(e, interface, device.address) == True:
                return True

        return False


async def discover_new_devices():
    client = DiscoveryClient()
    await client.discover()
