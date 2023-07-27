import datetime
import logging
from aiohttp import web
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.models.interface import ObjectInterface
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/keychains')
@login_required
async def get_list(request):
    objects = await ObjectInterface(Keychain).get_all()

    if not objects:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    return web.json_response({
        "status": "ok", "msg": [o.as_dict() for o in objects]}, status=200)


@routes.post('/api/v1.0/keychains')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = KeychainSchema()
    data = schema.load(jsondata)

    try:
        obj = Keychain(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        logger.warning(x)
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.get('/api/v1.0/keychains/{pk}')
@login_required
async def get(request):
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Keychain).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.patch('/api/v1.0/keychains/{pk}')
@login_required
async def patch(request):
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = KeychainSchema()
    data = schema.load(jsondata)

    obj = await ObjectInterface(Keychain).update(pk, data)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/keychains/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(Keychain).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    if obj.protected is True:
        return web.json_response({
            "status": "error",
            "msg": "A protected keychain cannot be removed."
        }, status=404)

    await ObjectInterface(Keychain).delete(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=200)
