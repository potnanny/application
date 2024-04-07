import logging
import datetime
import copy
from peewee import fn
from potnanny.utils import iso_from_sqlite
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.models.keychain import Keychain
from potnanny.database import db


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
        },
    },
    'data': {
        'datasets': []
    }
}


async def room_graph(pk:int, mtype:str, hours:int = 12):
    """
    Get graph data for room
    """

    try:
        kc = await Keychain.select().where(Keychain.name == 'settings').first()
        hours = kc.attributes['graph_hours']
    except:
        pass

    now = datetime.datetime.utcnow()
    start = str(now - datetime.timedelta(hours=hours))
    graph = copy.deepcopy(DEFAULT_GRAPH)

    # one label tick per hour only
    # graph['options']['scales']['xAxes']['ticks']['maxTicksLimit'] = hours

    sql = """
        SELECT
          d.id, d.name, m.type, m.value, m.created
        FROM
          measurement as m,
          device as d
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
            m.created"""

    data = {}
    labels = []
    async with db.connection():
        rows = await db.fetchall(sql)

    # first, built labels
    for r in rows:
        try:
            dt = iso_from_sqlite(r[4])
            labels.append(dt)
        except:
            pass

    labels = sorted(list(set(labels)))
    graph['data'].update({'labels': labels})

    for r in rows:
        if graph['options']['plugins']['title']['text'] is None:
            graph['options']['plugins']['title']['text'] = mtype.upper()

        if r[0] not in data:
            data[r[0]] = {
                'label': r[1],
                'data': [{'y': None, 'x': t} for t in labels] }
        dt = iso_from_sqlite(r[4])
        for item in data[r[0]]['data']:
            if item['x'] == dt:
                item['y'] = r[3]
                break

    # graph['data']['labels'] = sorted(list(set(labels)))
    graph['data']['labels'] = sorted(labels)
    graph['data']['datasets'] = [v for v in data.values()]

    return graph


async def device_graph(pk:int, mtype:str, hours:int = 12):
    """
    Get graph data for device
    """

    try:
        kc = await Keychain.select().where(Keychain.name == 'settings').first()
        hours = kc.attributes['graph_hours']
    except:
        pass

    now = datetime.datetime.utcnow()
    start = str(now - datetime.timedelta(hours=hours))
    graph = copy.deepcopy(DEFAULT_GRAPH)

    # one label tick per hour only
    # graph['options']['scales']['xAxes']['ticks']['maxTicksLimit'] = hours

    sql = """
        SELECT
          d.id, d.name, m.type, m.value, m.created
        FROM
          measurement as m,
          device as d
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
    async with db.connection():
        rows = await db.fetchall(sql)

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
