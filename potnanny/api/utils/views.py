import logging
from quart import Blueprint, render_template, jsonify, request
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.controllers.discover import discover_new_devices
from potnanny.controllers.worker import restart_worker
from potnanny.utils.serial import load_serial_number


logger = logging.getLogger(__name__)
bp = Blueprint('utils', __name__)


@bp.route('/api/v1.0/scan', methods=['GET'])
@login_required
async def scan_devices():
    results = await discover_new_devices()
    if not results:
        return jsonify({"status": "error", "msg": "unexpected failure"}), 404

    return jsonify({"status": "ok", "msg": results}), 200


@bp.route('/api/v1.0/restartworker', methods=['POST'])
@login_required
async def restart():
    results = await restart_worker()
    return jsonify({"status": "ok", "msg": "restarted"}), 200


@bp.route('/api/v1.0/serial', methods=['GET'])
@login_required
async def serial():
    result = await load_serial_number()
    return jsonify({"status": "ok", "msg": result}), 200
