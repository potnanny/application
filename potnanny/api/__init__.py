import os
import asyncio
import logging
import jinja2
import aiohttp_jinja2
import aiohttp_cors
import base64
from cryptography.fernet import Fernet
from aiohttp import web
from aiohttp_session import setup, SimpleCookieStorage
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from .index import routes as index_routes
from .auth import routes as auth_routes
from .users import routes as user_routes
from .keychains import routes as keychain_routes
from .rooms import routes as room_routes
from .devices import routes as device_routes
from .environments import routes as environment_routes
from .settings import routes as setting_routes
from .actions import routes as action_routes
from .controls import routes as control_routes
from .schedules import routes as schedule_routes
from .utils import routes as util_routes
from .plugins import routes as plugin_routes
from .tests import routes as test_routes
from .wifi import routes as wifi_routes


logger = logging.getLogger(__name__)


def init_api():
    logger.debug("Initializing Web API")

    app = web.Application()

    # setup static path handling
    app['static_root_url'] = '/static'
    static_path = os.path.join(os.path.dirname(__file__), "static")
    app.router.add_static('/static', static_path, name='static')

    # simple cookie storage for devel ONLY
    # setup(app, SimpleCookieStorage())

    # session cookie storage
    key = Fernet.generate_key()
    secret = base64.urlsafe_b64decode(key)
    setup(app, EncryptedCookieStorage(secret,
        cookie_name='POTNANNY_API',
        samesite="None",
        secure=True
        )
    )

    # plug in jinja template handling
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")))

    # add routing to endpoints
    app.add_routes(index_routes)
    app.add_routes(auth_routes)
    app.add_routes(user_routes)
    app.add_routes(room_routes)
    app.add_routes(device_routes)
    app.add_routes(keychain_routes)
    app.add_routes(environment_routes)
    app.add_routes(setting_routes)
    app.add_routes(util_routes)
    app.add_routes(plugin_routes)
    app.add_routes(action_routes)
    app.add_routes(control_routes)
    app.add_routes(schedule_routes)
    app.add_routes(test_routes)
    app.add_routes(wifi_routes)


    logger.debug("Building CORS routes")
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

    return app
