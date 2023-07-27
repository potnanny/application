import logging
from aiohttp import web
from potnanny.models.device import Device, DeviceSchema
from potnanny.models.interface import ObjectInterface
from potnanny.controllers.device import get_device_mtypes
from potnanny.controllers.outlet import switch_device_outlet
from potnanny.controllers.worker import Worker
from potnanny.controllers.graph import device_graph
from potnanny.locks import LOCKS
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/devices')
@login_required
async def get_list(request):
    objects = await ObjectInterface(Device).get_all()
    if not objects:
        return web.json_response({
            "status": "error", "msg": "object not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": [o.as_dict()  for o in objects] }, status=200)


@routes.post('/api/v1.0/devices')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = DeviceSchema()
    data = schema.load(jsondata)
    try:
        obj = Device(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.get('/api/v1.0/devices/{pk}')
@login_required
async def get(request):
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Device).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.patch('/api/v1.0/devices/{pk}')
@login_required
async def patch(request):
    changed = 0
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = DeviceSchema()
    data = schema.load(jsondata)

    obj = await ObjectInterface(Device).update(pk, data)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/devices/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    await ObjectInterface(Device).delete(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=200)


@routes.get('/api/v1.0/devices/{pk}/measurement-types')
@login_required
async def get_measurement_types(request):
    pk = int(request.match_info['pk'])
    results = await get_device_mtypes(pk)
    if not results:
        return web.json_response({
            "status": "error", "msg": f"device id {pk} no measurements"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": results}, status=200)


@routes.post('/api/v1.0/devices/{pk}/poll')
@login_required
async def device_poll(request):
    pk = int(request.match_info['pk'])
    worker = Worker()
    await worker.poll_device(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=200)


@routes.post('/api/v1.0/devices/{pk}/{outlet}/on')
@login_required
async def device_on(request):
    pk = int(request.match_info['pk'])
    outlet = int(request.match_info['outlet'])
    state = 1
    result = await switch_device_outlet(pk, outlet, state)
    if result is None or result != state:
        return web.json_response({
            "status": "error", "msg": f"error switching device {pk} outlet {outlet}"},
            status=500)

    return web.json_response({
        "status": "ok", "msg": {'state': state}}, status=200)


@routes.post('/api/v1.0/devices/{pk}/{outlet}/off')
@login_required
async def device_off(request):
    pk = int(request.match_info['pk'])
    outlet = int(request.match_info['outlet'])
    state = 0
    result = await switch_device_outlet(pk, outlet, state)
    if result is None or result != state:
        return web.json_response({
            "status": "error", "msg": f"error switching device {pk} outlet {outlet}"},
            status=500)

    return web.json_response({
        "status": "ok", "msg": {'state': state}}, status=200)


@routes.get('/api/v1.0/devices/{pk}/keycode')
@login_required
async def get_keycode(request):
    pk = int(request.match_info['pk'])
    device = await ObjectInterface(Device).get_by_id(pk)
    if not device:
        return web.json_response({
            "status": "error", "msg": "not found"}, status=404)

    if (not hasattr(device.plugin, 'is_key_required') or
        device.plugin.is_key_required is not True):
        return web.json_response({
            "status": "error", "msg": "not a valid request for this device"},
                status=405)

    secret = None
    try:
        if 'bluetooth' in LOCKS and LOCKS['bluetooth'] is not None:
            async with LOCKS['bluetooth'] as lock:
                secret = await device.plugin.scan_key()
        else:
            secret = await device.plugin.scan_key()
    except Exception as x:
        logger.debug(x)

    if secret:
        return web.json_response({
            "status": "ok", "msg": secret}, status=200)
    else:
        return web.json_response({
            "status": "error", "msg": "key code not detected before timeout"},
            status=404)


@routes.get('/api/v1.0/devices/{pk}/graph')
@login_required
async def graph(request):
    pk = int(request.match_info['pk'])
    mtype = request.rel_url.query.get('measurement', None)
    hours = int(request.rel_url.query.get('hours', 8))

    mygraph = await device_graph(pk, hours, mtype)
    if not mygraph:
        return web.json_response({
            "status": "error", "msg": "no data"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": mygraph}, status=200)
