import asyncio
import logging
import potnanny.database as database
from potnanny.config import Config
from potnanny.api import init_application
from potnanny.controllers.worker import (WORKER_STOP, run_worker,
    restart_worker, stop_worker)
from potnanny.utils import resolve_path, load_serial_number


# globals #
logger = logging.getLogger(__name__)
WEB_TASK = None
WRKR_TASK = None


async def run_app(config=Config()):
    """
    Initialize and run the app
    """
    global WEB_TASK
    global WRKR_TASK

    # load sn into global
    await load_serial_number()

    # init db and tables
    await database.init_db(config.database_uri, pragmas=(('foreign_keys','1'),))

    # the quart app
    application = init_application(config)

    # tasks to serve web with hypercorn, and run worker process
    WEB_TASK = asyncio.create_task(application.run_task(port=8080))
    WRKR_TASK = asyncio.create_task(restart_worker())

    logger.debug(f"web task: {WEB_TASK}")
    logger.debug(f"worker task: {WRKR_TASK}")
    logger.debug("entering event loop sleep")

    while True:
        await asyncio.sleep(1)
