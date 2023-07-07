from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/api/v1.0/tests/200')
async def get_200(request):
    return web.json_response({
        "status": "ok", "msg": "test 200 ok"}, status=200)

@routes.get('/api/v1.0/tests/401')
async def get_401(request):
    return web.json_response({
        "status": "error", "msg": "test not authorized"}, status=401)


@routes.get('/api/v1.0/tests/403')
async def get_403(request):
    return web.json_response({
        "status": "error", "msg": "test forbidden"}, status=403)


@routes.get('/api/v1.0/tests/404')
async def get_403(request):
    return web.json_response({
        "status": "error", "msg": "test not found"}, status=404)
