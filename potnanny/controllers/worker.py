import datetime
import logging
import asyncio
from potnanny.utils import utcnow, load_plugins
from potnanny.models.device import Device
from potnanny.models.keychain import Keychain
from potnanny.models.interface import ObjectInterface
from potnanny.locks import LOCKS
from potnanny.events import WORKER_EVENT
from potnanny.controllers.poll import Poller
from potnanny.controllers.schedule import run_schedules
from potnanny.controllers.cleanup import purge_measurements


logger = logging.getLogger(__name__)
TASK = None

async def run_worker():
    """
    Convenience function, to run the worker
    """
    global TASK
    logger.debug("Starting worker task")
    worker = Worker()
    TASK = asyncio.create_task(worker.run())


async def stop_worker():
    """
    Convenience function, to signal worker to stop
    """
    logger.debug("Stopping worker task")
    WORKER_EVENT.set()


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
        try:
            obj = await ObjectInterface(Keychain).get_by_name('settings')
            for k, v in obj.attributes.items():
                if hasattr(self, k):
                    setattr(self, k, v)
                elif k == 'temperature_display':
                    if v in ['f','F']:
                        self.convert_c = True
        except:
            pass


    async def load_plugins(self):
        load_plugins(self.plugin_path)


    async def run(self):
        await self.load_settings()
        await self.load_plugins()

        while not WORKER_EVENT.is_set():
            unow = datetime.datetime.utcnow().replace(microsecond=0)

            # at midnight we clean old records
            if unow.hour == 0 and unow.minute == 0 and unow.second == 0:
                start = unow - datetime.timedelta(days=self.storage_days)
                logger.debug(f"cleaning up measurements older than {start}")
                t1 = asyncio.create_task(purge_measurements(start))

            if unow.second == 0:
                # run schedules at top of every minute
                t2 = asyncio.create_task(run_schedules())

                # poll devices at intervals
                if unow.minute % self.polling_interval == 0:
                    t3 = asyncio.create_task(self.poll_devices())

            await asyncio.sleep(1)


    async def poll_devices(self):
        """
        poll active devices for information
        """

        logger.debug("polling devices")
        opts = {
            'convert_c': self.convert_c,
            'leaf_offset': self.leaf_offset}

        p = Poller(**opts)
        await p.poll()


    async def poll_device(self, pk: int):
        """
        poll device for information
        """

        logger.debug(f"polling device {pk}")
        opts = {
            'convert_c': self.convert_c,
            'leaf_offset': self.leaf_offset}

        p = Poller(**opts)
        await p.poll_id(pk)
