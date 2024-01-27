import asyncio
import logging
import datetime
from potnanny.database import db
from potnanny.models.measurement import Measurement


logger = logging.getLogger(__name__)


async def purge_measurements(cutoff:datetime.datetime):
    """
    Remove measurements from table when older than cutoff datetime
    """

    try:
        async with db.connection():
            query = Measurement.delete().where(Measurement.created < cutoff)
            results = await query.execute()
    except Exception as x:
        logger.warning(x)
