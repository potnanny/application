import asyncio
import random
import bleak
import logging
import datetime
import itertools
from potnanny.ble import lock
from potnanny.utils import utcnow
from potnanny.models.device import Device
from potnanny.controllers.pipeline import Pipeline
from .parser import Parser


logger = logging.getLogger(__name__)


class Collector:

    def __init__(self, *args, **kwargs):
        self.convert_c = False
        self.leaf_offset = -2
        self.devices = []
        self.now = utcnow()

        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


    async def collect(self):
        """
        Collect measurements from bluetooth devices, and send to pipeline
        """

        measurements = []
        results = {}
        if not self.devices:
            await self.load_devices()

        readers = self.get_reader_list(self.devices)
        clients = self.get_poller_list(self.devices)

        if readers:
            data = await self.scan_advertised(readers)
            if data:
                results.update(data)

        if clients:
            data = await self.poll_clients(clients)
            if data:
                results.update(data)

        if results:
            opts = {
                'leaf_offset': self.leaf_offset,
                'convert_c': self.convert_c,
                'now': self.now}
            measurements = Parser(**opts).parse(results)
            logger.debug("MEASUREMENTS: %s" % measurements)

            # send the measurements into the pipeline
            p = Pipeline()
            await p.input(measurements)

        return measurements


    async def collect_id(self, pk:int):
        await self.load_devices(pk)
        return await self.collect()


    def get_reader_list(self, devices:list) -> list:
        """
        parse list of devices and return only ble advertisement readers
        """

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


    def get_poller_list(self, devices:list) -> list:
        """
        parse list of devices and return only ble pollable clients
        """

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


    async def load_devices(self, ids:list = None):

        if ids is None:
            self.devices = await Device.select().where(Device.room_id != None)
        elif isinstance(ids, int):
            result = await Device.get_by_id(ids)
            self.devices = [result]
        elif isinstance(ids, list):
            self.devices = await Device.select().where(Device.id.in_(ids))

        return


    async def scan_advertised(self, devices:list, seconds:int = 40) -> dict:
        stop = asyncio.Event()
        timeout = self.now + datetime.timedelta(seconds=seconds)
        found = {d.id:None for d in devices}

        def callback(reporting, advertisement):
            addr = reporting.address
            for d in devices:
                try:
                    if found[d.id] is not None:
                        continue

                    if d.attributes['address'].upper() != addr.upper():
                        continue

                    results = d.read_advertisement(
                        reporting, advertisement)

                    if results is not None:
                        found[d.id] = results
                        break
                except:
                    pass

            if None not in found.values() and not stop.is_set():
                stop.set()


        while not stop.is_set() and datetime.datetime.now() < timeout:
            async with lock:
                async with bleak.BleakScanner(callback):
                    await asyncio.sleep(1)

        return found


    async def poll_clients(self, devices:list) -> dict:
        results = {d.id:None for d in devices}

        for d in devices:
            tries = 3
            success = False
            while tries and not success:
                logger.debug(f"Polling client {d.as_dict()}")
                data = None
                try:
                    async with lock:
                        data = await d.poll()
                        logger.debug(f"polled data: {data}")
                        if data is not None:
                            results[d.id] = data
                            success = True
                except Exception as x:
                    logger.warning(x)

                if not success:
                    tries -= 1

                await asyncio.sleep(random.random())

        return results
