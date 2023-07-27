import aiohttp_jinja2
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}
