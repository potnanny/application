import logging
from aiohttp import web
from potnanny.utils import iso_from_sqlite
from potnanny.models.room import Room, RoomSchema
from potnanny.models.interface import ObjectInterface
from potnanny.controllers.graph import room_graph
from .decorators import login_required


routes = web.RouteTableDef()
logger = logging.getLogger(__name__)


@routes.get('/api/v1.0/rooms')
@login_required
async def get_list(request):
    objects = await ObjectInterface(Room).get_all()
    if not objects:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    payload = [o.as_dict() for o in objects]

    return web.json_response({
        "status": "ok", "msg": payload}, status=200)


@routes.post('/api/v1.0/rooms')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = RoomSchema()
    data = schema.load(jsondata)

    try:
        obj = Room(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.get('/api/v1.0/rooms/{pk}')
@login_required
async def get(request):
    payload = None
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Room).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.patch('/api/v1.0/rooms/{pk}')
@login_required
async def patch(request):
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = RoomSchema()
    data = schema.load(jsondata)

    obj = await ObjectInterface(Room).update(pk, data)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/rooms/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    await ObjectInterface(Room).delete(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=202)


@routes.get('/api/v1.0/rooms/{pk}/graph')
@login_required
async def graph(request):
    pk = int(request.match_info['pk'])
    mtype = request.rel_url.query.get('measurement', None)
    hours = int(request.rel_url.query.get('hours', 8))

    graph = await room_graph(pk, mtype, hours)
    if not graph:
        return web.json_response({
            "status": "error", "msg": "no data"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": graph}, status=200)
