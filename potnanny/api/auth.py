import logging
import datetime
from aiohttp import web
from aiohttp_session import get_session, new_session
from potnanny.utils import verify_password
from potnanny.models.user import User
from potnanny.models.interface import ObjectInterface
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.post('/api/v1.0/login')
async def login(request):
    data = await request.json()
    user = await ObjectInterface(User).get_by_name(data['username'])

    if not user or not verify_password(data['password'], user.password):
        return web.json_response({
            "status": "error", "msg": "login failed"}, status=401)

    session = await new_session(request)
    session['username'] = user.name
    session['roles'] = user.roles
    session.changed()

    return web.json_response({
        "status": "ok", "msg": "authenticated ok"}, status=200)


@routes.post('/api/v1.0/logout')
@login_required
async def logout(request):
    session = await get_session(request)
    session.invalidate()

    return web.json_response({
        "status": "ok", "msg": "logged out"}, status=200)
