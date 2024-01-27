import logging
from quart import Blueprint, jsonify, request
from quart_auth import login_required
from .controllers import room_graph, device_graph


logger = logging.getLogger(__name__)
bp = Blueprint('graphs', __name__)


@bp.route('/api/v1.0/rooms/<int:pk>/graph', methods=['GET'])
@login_required
async def room(pk):
    try:
        hours = int(request.args.get('hours'))
    except:
        hours = 12

    try:
        mtype = request.args.get('measurement')
    except:
        mtype = None

    graph = await room_graph(pk, mtype, hours)
    if not graph:
        return jsonify({
            "status": "error", "msg": "no data"}), 404

    return jsonify({"status": "ok", "msg": graph}), 200


@bp.route('/api/v1.0/devices/<int:pk>/graph', methods=['GET'])
@login_required
async def device(pk):
    try:
        hours = int(request.args.get('hours'))
    except:
        hours = 12

    try:
        mtype = request.args.get('measurement')
    except:
        mtype = None

    logger.debug(f"devices graph measurement params: {pk} {mtype} {hours}")

    graph = await device_graph(pk, mtype, hours)
    if not graph:
        return jsonify({
            "status": "error", "msg": "no data"}), 404

    return jsonify({"status": "ok", "msg": graph}), 200
