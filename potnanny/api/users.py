import logging
from aiohttp import web
from potnanny.models.user import User
from potnanny.models.interface import ObjectInterface
from potnanny.utils import hash_password
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/users')
@login_required
async def get_list(request):
    objects = await ObjectInterface(User).get_all()
    if not objects:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)
    return web.json_response({
        "status": "ok", "msg": [o.as_dict() for o in objects]}, status=200)


@routes.get('/api/v1.0/users/{pk}')
@login_required
async def get(request):
    pk = int(request.match_info['pk'])
    obj = await ObjectInterface(User).get_by_id(pk)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.post('/api/v1.0/users')
@login_required
async def create(request):
    jsondata = await request.json()
    schema = UserSchema()
    data = schema.load(jsondata)
    if 'password' in data:
        data['password'] = hash_password(data['password'])

    try:
        obj = User(**data)
        await obj.insert()
        return web.json_response({
            "status": "ok", "msg": obj.as_dict()}, status=201)
    except Exception as x:
        return web.json_response({
            "status": "error", "msg": str(x) }, status=500)


@routes.patch('/api/v1.0/users/{pk}')
@login_required
async def patch(request):
    pk = int(request.match_info['pk'])
    jsondata = await request.json()
    schema = UserSchema()
    data = schema.load(jsondata)
    if 'password' in data:
        data['password'] = hash_password(data['password'])

    obj = await ObjectInterface(User).update(pk, data)
    if not obj:
        return web.json_response({
            "status": "error", "msg": f"object with id {pk} not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict()}, status=200)


@routes.delete('/api/v1.0/users/{pk}')
@login_required
async def delete(request):
    pk = int(request.match_info['pk'])
    await ObjectInterface(User).delete(pk)
    return web.json_response({
        "status": "ok", "msg": ""}, status=200)
