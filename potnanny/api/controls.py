import logging
from aiohttp import web
from marshmallow import fields
from potnanny.models.control import Control, ControlSchema
from potnanny.models.interface import ObjectInterface
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/controls')
@login_required
async def get_list(request):
    params = request.rel_url.query
    objects = await ObjectInterface(Control).get_all()
    if not objects:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    payload = [o.as_dict() for o in objects]
    return web.json_response({
        "status": "ok", "msg": payload}, status=200)


@routes.post('/api/v1.0/controls')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = ControlSchema()
    data = schema.load(jsondata)

    try:
        obj = Control(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.get('/api/v1.0/controls/{pk}')
@login_required
async def get(request):
    payload = None
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Control).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.patch('/api/v1.0/controls/{pk}')
@login_required
async def patch(request):
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = ControlSchema()
    data = schema.load(jsondata)
    obj = await ObjectInterface(Control).update(pk, data)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/controls/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    await ObjectInterface(Control).delete(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=200)
