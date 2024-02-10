import asyncio
import logging
import json
import potnanny.controllers.worker as worker
from quart import (Blueprint, jsonify, render_template, abort, request, flash,
    redirect)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.device import Device, DeviceSchema
from potnanny.models.room import Room
from potnanny.models.keychain import Keychain
from potnanny.database import db, lock
from potnanny.ble import lock as ble_lock
from potnanny.controllers.outlet import switch_device_outlet


logger = logging.getLogger(__name__)
bp = Blueprint('devices', __name__, template_folder='templates')


@bp.route('/devices', methods=['GET'])
@login_required
async def index():
    devices = await Device.select()
    try:
        features = await Keychain.select().where(Keychain.name == 'features')[0]
        logger.debug(features)
    except:
        features = None

    try:
        return await render_template('devices/index.html',
            data=devices, features=features)
    except TemplateNotFound:
        abort(404)


@bp.route('/api/v1.0/devices', methods=['GET'])
@login_required
async def get_list():
    objects = await Device.select()
    if not objects:
        return jsonify({"status": "error", "msg": "object not found"}), 404

    return jsonify({
        "status": "ok", "msg": [o.as_dict()  for o in objects] }), 200


@bp.route('/api/v1.0/devices', methods=['POST'])
@login_required
async def create():
    try:
        jsondata = await request.get_json()
        schema = DeviceSchema()
        data = schema.load(jsondata)
        async with lock:
            async with db.connection():
                obj = await Device.create(**data)
                await obj.save()
        return jsonify({"status": "ok", "msg": obj.as_dict()}), 201
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x) }), 500


@bp.route('/api/v1.0/devices/<int:pk>', methods=['GET'])
@login_required
async def get(pk):
    obj = await Device.get_by_id(pk)
    if not obj:
        return jsonify(
            {"status": "error", "msg": f"object with id {pk} not found"}), 404

    return jsonify({"status": "ok", "msg": obj.as_dict()}), 200


@bp.route('/api/v1.0/devices/<int:pk>', methods=['PATCH'])
@login_required
async def patch(pk):
    try:
        jsondata = await request.get_json()
        schema = DeviceSchema()
        data = schema.load(jsondata)
        async with lock:
            async with db.connection():
                obj = await Device.get_by_id(pk)
                for k, v in data.items():
                    setattr(obj, k, v)
                await obj.save()

        return jsonify({"status": "ok", "msg": obj.as_dict()}), 200
    except Exception as x:
        logger.warning(str(x))
        return jsonify(
            {"status": "error", "msg": f"object with id {pk} not found"}), 404


@bp.route('/api/v1.0/devices/<int:pk>', methods=['DELETE'])
@login_required
async def delete(pk):
    async with lock:
        async with db.connection():
            try:
                obj = await Device.get_by_id(pk)
                await obj.delete_instance()
                await flash("Device deleted", "info")
            except:
                pass

    return jsonify({
        "status": "ok", "msg": ""}), 200


@bp.route('/api/v1.0/devices/<int:pk>/poll', methods=['POST'])
@login_required
async def device_poll(pk):
    asyncio.create_task(worker.WORKER.poll_device(pk))
    return jsonify({"status": "ok", "msg": "polling queued"}), 200


@bp.route('/api/v1.0/devices/<int:pk>/<int:outlet>/on', methods=['POST'])
@login_required
async def device_on(pk, outlet):
    state = 1
    result = await switch_device_outlet(pk, outlet, state)
    if result != state:
        return jsonify({
            "status": "error",
            "msg": f"error switching device {pk} outlet {outlet}"}), 500

    return jsonify({"status": "ok", "msg": {'state': state}}), 200


@bp.route('/api/v1.0/devices/<int:pk>/<int:outlet>/off', methods=['POST'])
@login_required
async def device_off(pk, outlet):
    state = 0
    result = await switch_device_outlet(pk, outlet, state)
    if result != state:
        return jsonify({
            "status": "error",
            "msg": f"error switching device {pk} outlet {outlet}"}), 500

    return jsonify({"status": "ok", "msg": {'state': state}}), 200


@bp.route('/api/v1.0/devices/<int:pk>/keycode', methods=['GET'])
@login_required
async def get_keycode(pk):
    device = await Device.get_by_id(pk)
    if not device:
        return jsonify({
            "status": "error", "msg": "not found"}), 404

    if (not hasattr(device.plugin, 'is_key_required') or
        device.plugin.is_key_required is not True):
        return jsonify({
            "status": "error",
            "msg": "not a valid request for this device"}), 405

    secret = None
    try:
        async with ble_lock:
            secret = await device.plugin.scan_key()
    except Exception as x:
        logger.debug(x)

    if secret:
        return jsonify({"status": "ok", "msg": secret}), 200
    else:
        return jsonify({
            "status": "error",
            "msg": "key code not detected before timeout"}), 404
