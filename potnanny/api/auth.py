import logging
from aiohttp import web
from aiohttp_session import get_session, new_session
from potnanny.utils import verify_password, hash_password
from potnanny.models.user import User
from potnanny.models.keychain import Keychain
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

    resp = web.json_response({
        "status": "ok", "msg": "authenticated ok"}, status=200)

    """
    # for optional features
    try:
        kc = await ObjectInterface(Keychain).get_by_name('features')
        ck = {
            'username': user.name,
            'roles': user.roles }

        ck['room_limit'] = kc.attributes['room_limit']
        ck['device_limit'] = kc.attributes['device_limit']
        resp.set_cookie("POTNANNY", ck, samesite="None", secure=False)
    except Exception as x:
        logger.warning(x)
        pass
    """

    return resp


@routes.post('/api/v1.0/logout')
@login_required
async def logout(request):
    session = await get_session(request)
    session.invalidate()

    return web.json_response({
        "status": "ok", "msg": "logged out"}, status=200)


@routes.post('/api/v1.0/pwreset')
@login_required
async def pwreset(request):
    """
    reset password. requires data:
        username:
        current: (current password for user)
        password: (new password for user)
    """

    data = await request.json()
    logger.debug(data)

    # missing required data?
    for k in ['username','password','current']:
        if k not in data:
            return web.json_response({
                "status": "error", "msg": f"field {k} must be provided"},
                status=400)

    # user exists?
    user = await ObjectInterface(User).get_by_name(data['username'])
    if not user:
        return web.json_response({
            "status": "error", "msg": f"username {data['username']} not found"},
            status=404)

    # invalid current password?
    match = verify_password(data['current'], user.password)
    if not match:
        return web.json_response({
            "status": "error", "msg": f"bad password"},
            status=403)

    # hash the password and update the user
    opts = {'password': hash_password(data['password'])}
    obj = await ObjectInterface(User).update(user.id, opts)
    return web.json_response({
        "status": "ok", "msg": "password reset successfully"}, status=200)
