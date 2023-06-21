from sqlalchemy.sql import text
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.models.interface import execute_statement


async def get_device_mtypes(pk):
    stmt = text("""
        SELECT
            m.type
        FROM
            measurements as m
        WHERE
            m.device_id = %d
        GROUP BY
            m.type
        ORDER BY
            m.type ASC
    """ % pk)

    try:
        rows = await execute_statement(stmt)
        return [r[0] for r in rows.all()]
    except:
        return []
