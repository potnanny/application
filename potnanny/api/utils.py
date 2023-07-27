import logging
from aiohttp import web
from potnanny.utils.shell import run
from potnanny.controllers.discover import discover_new_devices
from potnanny.controllers.worker import restart_worker
from potnanny.utils.serial import load_serial_number
from potnanny.utils.network import aio_has_www
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/ping')
async def ping(request):
    return web.json_response({
        "status": "ok", "msg": "pong"}, status=200)


@routes.get('/api/v1.0/scan')
@login_required
async def scan(request):
    results = await discover_new_devices()
    return web.json_response({
        "status": "ok", "msg": results}, status=200)


@routes.post('/api/v1.0/reboot')
@login_required
async def reboot(request):
    (rval, stdout, stderr) = await run('sudo reboot now')


@routes.get('/api/v1.0/serial')
@login_required
async def serial_number(request):
    sn = await load_serial_number()
    return web.json_response({
            "status": "ok", "msg": sn }, status=200)


@routes.get('/api/v1.0/internet')
@login_required
async def has_internet(request):
    success = await aio_has_www()
    if success:
        return web.json_response({
                "status": "ok", "msg": "internet connection" }, status=200)
    else:
        return web.json_response({
                "status": "ok", "msg": "no internet connection" }, status=404)
