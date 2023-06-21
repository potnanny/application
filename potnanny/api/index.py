import aiohttp_jinja2
import jinja2
from aiohttp import web
from .decorators import login_required

routes = web.RouteTableDef()

@routes.get('/')
@aiohttp_jinja2.template('index.html')
@login_required
async def index(request):
    return {}
