import logging
import datetime
import copy
from sqlalchemy.sql import text
from potnanny.utils import iso_from_sqlite
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.models.interface import execute_statement


logger = logging.getLogger(__name__)


DEFAULT_GRAPH = {
    'type': 'line',
    'options': {
        'maintainAspectRatio': False,
        'responsive': True,
        'plugins': {
            'title': {
                'display': True,
                'text': None,
            }
        }
    },
    'data': {
        'datasets': []
    }
}


async def room_graph(pk: int, mtype: str, hours: int = 12):
    """
    Get graph data for room
    """

    now = datetime.datetime.utcnow()
    start = str(now - datetime.timedelta(hours=hours))
    graph = copy.deepcopy(DEFAULT_GRAPH);

    sql = """
        SELECT
          d.id, d.name, m.type, m.value, m.created
        FROM
          measurements as m,
          devices as d
        WHERE
            d.room_id = %d
        AND
            m.device_id = d.id
        AND
            m.created >= '%s'
    """ % (pk, start)

    if mtype is not None:
        sql += """
        AND
            m.type = '%s' """ % mtype

    sql += """
        ORDER BY
            m.created """

    data = {}
    labels = []
    results = await execute_statement(text(sql))
    rows = results.all()
    for r in rows:
        if graph['options']['plugins']['title']['text'] is None:
            graph['options']['plugins']['title']['text'] = mtype.upper()

        if r[0] not in data:
            data[r[0]] = {
                'label': r[1],
                'data': [] }
        dt = iso_from_sqlite(r[4])

        if dt not in labels:
            labels.append(dt)

        data[r[0]]['data'].append({
            'y': r[3],
            'x': dt,
        })

    # graph['data']['labels'] = sorted(list(set(labels)))
    graph['data']['labels'] = sorted(labels)
    graph['data']['datasets'] = [v for v in data.values()]

    return graph


async def device_graph(pk: int, hours: int = 12, mtype = None):
    """
    Get graph data for device
    """

    now = datetime.datetime.utcnow()
    start = str(now - datetime.timedelta(hours=hours))
    graph = copy.deepcopy(DEFAULT_GRAPH);

    sql = """
        SELECT
          d.id, d.name, m.type, m.value, m.created
        FROM
          measurements as m,
          devices as d
        WHERE
            d.id = %d
        AND
            m.device_id = d.id
        AND
            m.created >= '%s'
    """ % (pk, start)

    if mtype is not None:
        sql += """
        AND
            m.type = '%s' """ % mtype

    sql += """
        ORDER BY
            m.created """

    data = {}
    labels = []
    results = await execute_statement(text(sql))
    rows = results.all()
    for r in rows:
        if graph['options']['plugins']['title']['text'] is None:
            graph['options']['plugins']['title']['text'] = r[1]

        if r[2] not in data:
            data[r[2]] = {
                'label': r[2],
                'data': [] }
        dt = iso_from_sqlite(r[4])
        if dt not in labels:
            labels.append(dt)

        data[r[2]]['data'].append({
            'y': r[3],
            'x': dt,
        })

    graph['data']['labels'] = sorted(list(set(labels)))
    graph['data']['datasets'] = [v for v in data.values()]
    return graph
