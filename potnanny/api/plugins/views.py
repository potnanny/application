import asyncio
import logging
import json
from quart import (Blueprint, jsonify, render_template, abort, request, flash,
    redirect)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from .controllers import get_plugin_map


logger = logging.getLogger(__name__)
bp = Blueprint('plugins', __name__, template_folder='templates')


@bp.route('/plugins', methods=['GET'])
@login_required
async def index():
    data = await get_plugin_map()
    try:
        return await render_template('plugins/index.html',
            data=data,
            title=f"Installed Plugins")
    except TemplateNotFound:
        abort(404)


@bp.route('/api/v1.0/plugins', methods=['GET'])
@login_required
async def plugin_list():
    try:
        data = await get_plugin_map()
        return jsonify({
            "status": "ok", "msg": data }), 200
    except:
        return jsonify({
            "status": "error", "msg": 'no data' }), 404
