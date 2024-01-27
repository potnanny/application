import logging
from potnanny.database import db
from potnanny.plugins import BluetoothDevicePlugin
from potnanny.models.device import Device
from potnanny.utils.scanner import BLEScanner


logger = logging.getLogger(__name__)


class DiscoveryClient:
    def __init__(self, *args, **kwargs):
        self.scanner = BLEScanner()


    async def discover(self):
        results = []
        existing = await Device.select()
        found = await self.scanner.scan_devices()

        logger.debug(f"found devices: {found}")
        logger.debug(type(found))

        devices = self.recognized_devices([f for f in found])
        logger.debug(f"recognized devices: {devices}")
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

            logger.debug(f"new device: {opts}")
            results.append(opts)

        if results:
            async with db.connection():
                for d in results:
                    print(f"new device {d}")
                    try:
                        obj = await Device.create(**d)
                        await obj.save()
                    except Exception as x:
                        logger.warning(x)

        return results


    def recognized_devices(self, devices:list) -> list:
        """
        Return a filtered list of ble devices that we can communicate with.
        [(device, interface_name), ]
        """

        results = []
        for d in devices:
            fingerprint = {'address': d.address, 'name': d.name}
            logger.debug(f" device: {d}, fingerprint: {fingerprint}")

            for p in BluetoothDevicePlugin.plugins:
                attrs = None

                if p.recognize_this(fingerprint):
                    found = '.'.join((p.__module__, p.__name__))
                    try:
                        attrs = p.attributes
                    except:
                        attrs = {}

                    results.append((d, found, attrs))

        return results


    def is_existing_device(self, existing:list, device, interface):
        """
        Compare ble-device to list of existing devices, and see if match
        exists already
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
