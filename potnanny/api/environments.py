import logging
from aiohttp import web
from potnanny.controllers.environment import (get_environments,
    get_room_environments)
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/environments')
@login_required
async def all_environments(request):
    results = await get_environments()
    if not results:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    return web.json_response({
        "status": "ok", "msg": results}, status=200)


@routes.get('/api/v1.0/environments/{pk}')
@login_required
async def room_environment(request):
    pk = int(request.match_info['pk'])
    results = await get_room_environments(pk)
    if not results:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    return web.json_response({
        "status": "ok", "msg": results}, status=200)
