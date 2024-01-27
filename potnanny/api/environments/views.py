import logging
from quart import Blueprint, jsonify, render_template, abort
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.keychain import Keychain
from .controllers import get_environments, get_room_environments


logger = logging.getLogger(__name__)
bp = Blueprint('environments', __name__, template_folder='templates')


SUFFIXES = {
    'temperature': '°',
    'humidity': '%',
    'battery': '%',
    'soil_moisture': '%',
}


@bp.route('/', methods=['GET'])
@login_required
async def dashboard():
    data = await get_environments()
    try:
        features = await Keychain.select().where(Keychain.name == 'features')[0]
        logger.debug(features)
    except:
        features = None

    try:
        return await render_template('environments/dash.html',
            data=data,
            suffixes=SUFFIXES,
            features=features.as_dict())
    except TemplateNotFound:
        abort(404)


@bp.route('/environments/<int:pk>', methods=['GET'])
@login_required
async def room_dashboard(pk):
    data = await get_room_environments(pk)
    try:
        return await render_template('environments/room.html',
            data=data, suffixes=SUFFIXES)
    except TemplateNotFound:
        abort(404)


@bp.route('/api/v1.0/environments', methods=['GET'])
@login_required
async def environment():
    data = await get_environments()
    if data:
        return jsonify({'status': 'ok', 'msg': data}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'no data'}), 404


@bp.route('/api/v1.0/environments/<int:pk>', methods=['GET'])
@login_required
async def room_environment(pk):
    data = await get_room_environments(pk)
    if data:
        return jsonify({'status': 'ok', 'msg': data}), 200
    else:
        return jsonify({'status': 'error', 'msg': 'no data'}), 404
