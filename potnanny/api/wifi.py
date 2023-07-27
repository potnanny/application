import logging
import datetime
from aiohttp import web
from potnanny.utils.wifi import (wifi_networks, append_to_wpaconf,
    wpa_password_entry)
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/wifi/networks')
@login_required
async def get_networks(request):
    results = await wifi_networks()
    if not results:
        return web.json_response({
            "status": "error", "msg": "no data"}, status=404)

    return web.json_response({
        "status": "ok", "msg": results}, status=200)


@routes.post('/api/v1.0/wifi/join')
@login_required
async def join_network(request):
    data = await request.json()
    entry = await wpa_password_entry(data['ssid'], data['password'])
    rval, msg = await append_to_wpaconf(entry)

    if rval != 0:
        return web.json_response({
            "status": "error", "msg": f"error joining network: {msg}"},
            status=409)

    return web.json_response({
        "status": "ok", "msg": "reboot raspberry pi to join the new network"},
        status=201)
