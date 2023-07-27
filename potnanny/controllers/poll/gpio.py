import logging
from potnanny.locks import LOCKS


logger = logging.getLogger(__name__)


class GPIOInterface:

    def __init__(self, *args, **kwargs):
        self.lock = LOCKS['gpio']
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def poll_devices(self, devices):
        """
        poll measurements from list of devices

        args:
            - list of Device objects
        returns:
            - list of measurements
        """

        results = []

        # filter only gpio devices
        valid = self._gpio_list(devices)

        # run polling and gather results when done
        for d in valid:
            data = None
            try:
                if self.lock:
                    async with self.lock:
                        data = await d.poll()
                else:
                    data = await d.poll()
            except Exception as x:
                logger.warning(x)

            if data:
                results.append(data)

        return results


    def _gpio_list(self, devices):
        # parse list of devices and return only gpio pollable clients
        results = []
        for d in devices:
            if (not hasattr(d.plugin, 'is_gpio') or
                d.plugin.is_bluetooth is not True):
                continue

            if (not hasattr(d.plugin, 'is_pollable') or
                d.plugin.is_pollable is not True):
                continue

            results.append(d)

        return results
