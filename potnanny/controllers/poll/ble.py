import asyncio
import logging
import random
from potnanny.utils.scanner import BLEScanner


logger = logging.getLogger(__name__)


class BLEInterface(BLEScanner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # the reference to self.lock is inherited from BLEScanner
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def poll_devices(self, devices: list) -> list:
        """
        poll measurements from list of devices

        args:
            - list of Device objects
        returns:
            - list of measurements
        """

        results = []

        # divide into lists of Readers or Poller devices
        readers = self._reader_list(devices)
        clients = self._poller_list(devices)

        # run polling and gather results when done
        task_list = []
        if readers:
            task_list.append(self._poll_readers(readers))

        if clients:
            task_list.append(self._poll_clients(clients))

        results = await asyncio.gather(*task_list)
        return results


    def _reader_list(self, devices):
        # parse list of devices and return only ble advertisement readers
        results = []
        for d in devices:
            if (not hasattr(d.plugin, 'is_bluetooth') or
                d.plugin.is_bluetooth is not True):
                continue

            if (not hasattr(d.plugin, 'is_reader') or
                d.plugin.is_reader is not True):
                continue

            results.append(d)

        logger.debug("Reader List: %s" % results)
        return results


    def _poller_list(self, devices):
        # parse list of devices and return only ble pollable clients
        results = []
        for d in devices:
            if (not hasattr(d.plugin, 'is_bluetooth') or
                d.plugin.is_bluetooth is not True):
                continue

            if (not hasattr(d.plugin, 'is_pollable') or
                d.plugin.is_pollable is not True):
                continue

            results.append(d)

        logger.debug("Poller List: %s" % results)
        return results


    async def _poll_clients(self, devices):
        """
        poll devices that we connect to as a client

        args:
            - list of devices to collect for
        """

        results = []
        for d in devices:
            await asyncio.sleep(random.random())
            try:
                data = None
                if self.lock:
                    async with self.lock:
                        data = await d.poll()
                else:
                    data = await d.poll()

                if data is not None:
                    results.append(data)

            except Exception as x:
                logger.warning(x)

        return results


    async def _poll_readers(self, devices):
        """
        poll devices that Read Advertised Data(RAD) from bluetooth

        args:
            - list of devices to collect for
            - timestamp for collected measurements
        """

        results = []
        found = {d.id:None for d in devices}
        tries = 10
        success = False
        while tries and not success:
            addresses = [d.attributes['address'] for d in devices if (found[d.id] is None)]
            scans = await self.scan_advertised_filter(addresses)
            found.update(self._parse_advertised_data(devices, scans))

            if None not in found.values():
                success = True

            if not success:
                tries -= 1
                await asyncio.sleep(random.random())

        results += found.values()
        return results


    def _parse_advertised_data(self, devices, data):
        """
        parse advertisement results

        args:
            - list of devices
            - list of data points
        returns:
            dict of {
                device_id: measurement,
            }
        """

        results = {}
        for bundle in data:
            if bundle is None:
                continue
            reporting, advertisement = bundle
            fingerprint = {'address': reporting.address, 'name': reporting.name}
            for d in devices:
                if d.room_id is None:
                    continue

                if not d.plugin.__class__.recognize_this(fingerprint):
                    continue

                try:
                    if d.attributes['address'].upper() != reporting.address.upper():
                        continue
                except Exception as x:
                    logger.warning(x)
                    continue

                try:
                    data = d.read_advertisement(reporting, advertisement)
                    if data:
                        results[d.id] = data
                    else:
                        logger.warning("No data: Device:%d, Reporting:%s, Adv:%s" % (
                            d.id, reporting, advertisement))
                except Exception as x:
                    logger.warning(x)

        return results
