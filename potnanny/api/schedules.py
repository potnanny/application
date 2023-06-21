import logging
from aiohttp import web
from potnanny.models.schedule import Schedule, ScheduleSchema
from potnanny.models.interface import ObjectInterface
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/schedules')
@login_required
async def get_list(request):
    params = request.rel_url.query
    objects = await ObjectInterface(Schedule).get_all()
    if not objects:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    if params and 'device' in params:
        if 'outlet' in params:
            payload = [ o.as_dict() for o in objects if (
                o.device_id == int(params['device']) and
                o.outlet == int(params['outlet'])) ]
        else:
            payload = [
                o.as_dict() for o in objects if (
                o.device_id == int(params['device'])) ]
    else:
        payload = [
            o.as_dict() for o in objects]

    return web.json_response({
        "status": "ok", "msg": payload}, status=200)


@routes.post('/api/v1.0/schedules')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = ScheduleSchema()
    data = schema.load(jsondata)

    try:
        obj = Schedule(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.get('/api/v1.0/schedules/{pk}')
@login_required
async def get(request):
    payload = None
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Schedule).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.patch('/api/v1.0/schedules/{pk}')
@login_required
async def patch(request):
    changed = 0
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = DeviceSchema()
    data = schema.load(jsondata)

    obj = await ObjectInterface(Schedule).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    for k, v in data.items():
        if hasattr(obj, k) and getattr(obj, k) != v:
            setattr(obj, k, v)
            changed += 1

    if changed:
        try:
            await obj.update()
        except Exception as x:
            return web.json_response({
                "status": "error", "msg": str(x) }, status=500)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/schedules/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    await ObjectInterface(Schedule).delete(pk)
    return web.json_response({
            "status": "ok", "msg": ""}, status=200)
