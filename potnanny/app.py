import asyncio
import logging
import signal
import ssl
import potnanny.database as db
from aiohttp import web
from potnanny.config import Config
from potnanny.api import init_api
from potnanny.events import STOP_EVENT
from potnanny.controllers.worker import run_worker, stop_worker
from potnanny.locks import init_locks
from potnanny.utils import resolve_path, load_serial_number


logger = logging.getLogger(__name__)


def handle_kill(*args):
    """
    Gracefully allow asyncio processes to quit
    """

    STOP_EVENT.set()


async def init_app(config=Config()):
    """
    Initialize and run the app
    """

    # handle signal kill properly
    signal.signal(signal.SIGTERM, handle_kill)

    # load sn into global
    await load_serial_number()

    # init db and tables
    await db.init_db(config.database_uri)

    await init_locks()
    app = init_api()

    # add stop/start for the worker
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    runner = web.AppRunner(app)
    await runner.setup()

    # we run the webserver on 8080, and let nginx proxy handle the https/ssl
    site = web.TCPSite(runner, '0.0.0.0', port=8080)
    await site.start()

    while not STOP_EVENT.is_set():
        await asyncio.sleep(1)

    logger.debug("Exiting")
    await runner.cleanup()


async def on_startup(app):
    await run_worker()


async def on_cleanup(app):
    await stop_worker()
