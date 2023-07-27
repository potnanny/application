from functools import wraps
from aiohttp import web
from aiohttp_session import get_session

def login_required(func):
    @wraps(func)
    async def decorated(request):
        session = await get_session(request)
        if not session or session.new is True or 'username' not in session:
            return web.json_response({
                "status": "error", "msg": "session not authenticated"},
                status=401)

        return await func(request)

    return decorated
