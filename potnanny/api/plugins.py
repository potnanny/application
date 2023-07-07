import os
import logging
import datetime
import asyncio
from aiohttp import web
from potnanny.plugins import (BluetoothDevicePlugin, GPIODevicePlugin,
    PipelinePlugin, ActionPlugin)
from .decorators import login_required

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

@routes.get('/api/v1.0/plugins')
@login_required
async def get_plugins(request):
    results = {}

    try:
        results['bluetooth'] = [{
            'name': p.name,
            'description': p.description,
            'interface': '.'.join((p.__module__, p.__name__))
        } for p in BluetoothDevicePlugin.plugins]
    except:
        pass

    try:
        results['gpio'] = [{
            'name': p.name,
            'description': p.description,
            'interface': '.'.join((p.__module__, p.__name__))
        } for p in GPIODevicePlugin.plugins]
    except:
        pass

    try:
        results['pipeline'] = [{
            'name': p.name,
            'description': p.description,
            'interface': '.'.join((p.__module__, p.__name__))
        } for p in PipelinePlugin.plugins]
    except:
        pass

    try:
        results['action'] = [{
            'name': p.name,
            'description': p.description,
            'interface': '.'.join((p.__module__, p.__name__))
        } for p in ActionPlugin.plugins]
    except:
        pass

    return web.json_response({
        "status": "ok", "msg": results}, status=200)
