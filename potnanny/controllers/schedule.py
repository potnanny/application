import asyncio
import logging
import datetime
from potnanny.utils import utcnow
from potnanny.models.schedule import Schedule
from potnanny.models.interface import ObjectInterface

logger = logging.getLogger(__name__)


async def run_schedules(now=None):
    """
    Run scheduled actions
    """

    tasks = []
    if now is None:
        now = datetime.datetime.now().replace(second=0, microsecond=0)

    schedules = await ObjectInterface(Schedule).get_all()
    for s in schedules:
        try:
            if s.runs_now() is True:
                tasks.append(s.run(now))
        except Exception as x:
            logger.warning(str(x))

    if tasks:
        results = await asyncio.gather(*tasks)
