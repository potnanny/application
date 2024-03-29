import datetime
from potnanny.utils import iso_from_sqlite
from potnanny.database import db

async def get_environments() -> dict:
    """
    Get average Temp/Humidity/VPD readings for all rooms
    """

    stmt = """
        SELECT id,name,type,AVG(value),created FROM
            (SELECT id, name FROM room) AS a
            LEFT JOIN (
                SELECT
                    d.id as device_id,
                    d.room_id,
                    m.type,
                    m.value,
                    MAX(m.created) as created
                FROM
                    measurement AS m,
                    device AS d
                WHERE
                    m.device_id = d.id
                AND
                    m.type IN ('temperature', 'humidity', 'vpd')
                GROUP BY
                    d.room_id,
                    d.id,
                    m.type
            ) AS b
            ON a.id = b.room_id
            GROUP BY
                a.id,
                b.type
    """

    data = {}
    rows = []
    async with db.connection():
        rows = await db.fetchall(stmt)

    # reformat the row data
    for row in rows:
        if row[0] not in data:
            data[row[0]] = {
                'id': row[0],
                'name': row[1],
                'measurements': {} }

        if row[3] is not None:
            data[row[0]]['measurements'].update({ row[2]: row[3] })
            data[row[0]]['created'] = iso_from_sqlite(row[4])

    return [data[r] for r in sorted(data.keys())]


async def get_room_environments(pk:int) -> dict:
    """
    Get Device readings for all devices in a room
    """

    stmt = """
        SELECT * FROM
            (SELECT
                r.id AS room_id,
                r.name AS room_name,
                d.id as device_id,
                d.name as device_name
             FROM
                room as r,
                device as d
             WHERE
                r.id = %d
             AND
                d.room_id = %d) AS a
            LEFT JOIN (
                SELECT
                    m.device_id as m_device_id,
                    m.type,
                    m.value,
                    MAX(m.created)
                FROM
                    measurement AS m
                GROUP BY
                    m.device_id,
                    m.type
            ) AS b
            ON a.device_id = b.m_device_id
            ORDER BY
                a.device_id
    """ % (pk, pk)

    data = {}
    rows = []
    async with db.connection():
        rows = await db.fetchall(stmt)

    # reformat the row data
    for row in rows:
        if 'devices' not in data:
            data = {'id': row[0], 'name': row[1], 'devices': {}}

        if row[2] not in data['devices']:
            data['devices'][row[2]] = {
                'id': row[2],
                'name': row[3],
                'measurements': {} }

        if row[5] is not None:
            data['devices'][row[2]]['measurements'].update({ row[5]: row[6] })
            data['devices'][row[2]]['created'] = iso_from_sqlite(row[7])

    data['devices'] = [data['devices'][k] for k in sorted(data['devices'].keys())]
    return data
