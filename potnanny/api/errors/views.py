import asyncio
import logging
import json
from quart import (Blueprint, jsonify, render_template, abort, request, flash,
    redirect)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from .controllers import get_error_list


logger = logging.getLogger(__name__)
bp = Blueprint('errors', __name__, template_folder='templates')
try:
    ERR_PATH = logging.getLoggerClass().root.handlers[0].baseFilename
except:
    ERR_PATH = None


@bp.route('/errors', methods=['GET'])
@login_required
async def index():
    hours = 24
    errors = await get_error_list(ERR_PATH, hours, True)
    try:
        return await render_template('errors/index.html',
            data=errors,
            title=f"Errors from last {hours} hours")
    except TemplateNotFound:
        abort(404)


@bp.route('/api/v1.0/errors', methods=['GET'])
@login_required
async def get_list():
    errors = await get_error_list(ERR_PATH, 24, True)
    return jsonify({
        "status": "ok", "msg": errors}), 200
