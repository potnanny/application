# Potnanny Plugins


## Bluetooth
There are two types of bluetooth device interface plugins.
  1. Advertisement: a plugin that will extract data from the BLE Advertisement broadcast data.
  2. Polling: a plugin that will connect to the BLE device as a client to extract data.


### Advertisement Plugin
A plugin class that will decode BLE advertisement data must have a non-async method named *read_advertisement*, which accepts two arguments, *device*, and *advertisement data*.
```
import re
from potnanny.plugins import DevicePlugin
from potnanny.plugins.mixins import FingerprintMixin

class MyDevice(DevicePlugin, FingerprintMixin):
    fingerprint = {
        'address': re.compile('^A4:C1:38', re.IGNORECASE),
        'name': re.compile('^GVH', re.IGNORECASE) }

    def read_advertisement(self, device, advertisement):
        values = {}
        try:
            values = self._parse(advertisement)
        except:
            pass

        return values
```

### Polling Plugin
Must have an async method named *poll*, which does not accept any arguments.

```
import re
import asyncio
from bleak import BleakClient
from potnanny.plugins import DevicePlugin
from potnanny.plugins.mixins import FingerprintMixin

class MyDevice(DevicePlugin, FingerprintMixin):
    fingerprint = {
        'address': re.compile('^A4:C1:38', re.IGNORECASE),
        'name': re.compile('^GVH', re.IGNORECASE) }

    def __init__(self, *args, **kwargs):
        self.address = None
        allowed = ['address']
        for k, v in kwargs.items():
            if hasattr(self, k) and k in allowed:
                setattr(self, k, v)

        if self.address is None:
            raise ValueError("Device address required")

    async def poll(self):
        values = {}
        async with BleakClient(self.address) as client:
            try:
                values = await self._read(client)
            except:
                pass

        return values

```
