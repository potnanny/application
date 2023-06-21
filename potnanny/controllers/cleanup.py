import asyncio
import logging
from sqlalchemy import delete
from potnanny.models.interface import execute_statement
from potnanny.models.measurement import Measurement
from potnanny.models.error import Error


logger = logging.getLogger(__name__)


async def purge_measurements(cutoff):
    """
    Remove measurements from table when older than cutoff datetime
    """

    try:
        stmt = (delete(Measurement).where(Measurement.created < cutoff))
        result = await execute_statement(stmt)
    except Exception as x:
        logger.warning(x)

    try:
        stmt = (delete(Error).where(Error.created < cutoff))
        result = await execute_statement(stmt)
    except Exception as x:
        logger.warning(x)
