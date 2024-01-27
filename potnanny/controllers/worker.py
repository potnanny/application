import asyncio
import logging
import datetime
from threading import Event
from potnanny.utils import utcnow
from potnanny.plugins.utils import load_plugins
from potnanny.models.device import Device
from potnanny.models.keychain import Keychain
from potnanny.controllers.collector import Collector
from potnanny.controllers.cleanup import purge_measurements


logger = logging.getLogger(__name__)
WORKER = None
WORKER_STOP = Event()
TASK = None


async def run_worker():
    """
    Convenience function, to run the worker
    """

    global TASK
    global WORKER
    WORKER_STOP.clear()

    logger.debug("Starting worker task")
    WORKER = Worker()
    TASK = asyncio.create_task(WORKER.run())


async def stop_worker():
    """
    Convenience function, to signal worker to stop
    """

    logger.debug("Stopping worker task")
    WORKER_STOP.set()


async def restart_worker():
    """
    Convenience function, to stop and restart the worker
    """

    await stop_worker()
    while TASK in asyncio.all_tasks():
        await asyncio.sleep(1)

    await run_worker()


class Worker:
    def __init__(self, *args, **kwargs):
        self.convert_c = False
        self.leaf_offset = -2
        self.polling_interval = 10
        self.plugin_path = "~/potnanny/plugins"
        self.storage_days = 7


    async def load_settings(self):
        results = await Keychain.select().where(Keychain.name == 'settings')
        obj = results[0]
        for k, v in obj.attributes.items():
            if hasattr(self, k):
                setattr(self, k, v)
            elif k == 'temperature_display':
                if v in ['f','F']:
                    self.convert_c = True

        load_plugins(self.plugin_path)


    async def run(self):
        await self.load_settings()

        while not WORKER_STOP.is_set():
            now = datetime.datetime.utcnow().replace(microsecond=0)

            # at midnight we clean old records
            if now.hour == 0 and now.minute == 0 and now.second == 0:
                start = now - datetime.timedelta(days=self.storage_days)
                logger.debug(f"cleaning up measurements older than {start}")
                t1 = asyncio.create_task(purge_measurements(start))

            if now.second == 0:
                # poll devices at intervals
                if now.minute % self.polling_interval == 0:
                    t3 = asyncio.create_task(self.poll_devices())

            await asyncio.sleep(1)


    async def poll_devices(self):
        """
        poll active devices for information
        """

        logger.debug("polling all devices")
        opts = {
            'convert_c': self.convert_c,
            'leaf_offset': self.leaf_offset}

        c = Collector(**opts)
        asyncio.create_task(c.collect())


    async def poll_device(self, pk:int):
        """
        poll device for information
        """

        logger.debug(f"polling single device ({pk})")
        opts = {
            'convert_c': self.convert_c,
            'leaf_offset': self.leaf_offset}

        c = Collector(**opts)
        asyncio.create_task(c.collect_id(pk))
