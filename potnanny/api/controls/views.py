import asyncio
import logging
import json
from quart import (Blueprint, jsonify, render_template, abort, request, flash,
    redirect)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.control import Control, ControlSchema
from potnanny.database import db, lock

logger = logging.getLogger(__name__)
bp = Blueprint('controls', __name__)


@bp.route('/api/v1.0/controls', methods=['GET'])
@login_required
async def get_list():
    objects = await Control.select()
    if not objects:
        return jsonify({"status": "error", "msg": "object not found"}), 404

    return jsonify({
        "status": "ok", "msg": [o.as_dict()  for o in objects] }), 200


@bp.route('/api/v1.0/controls', methods=['POST'])
@login_required
async def create():
    try:
        jsondata = await request.get_json()
        schema = ControlSchema()
        data = schema.load(jsondata)
        async with lock:
            async with db.connection():
                obj = await Control.create(**data)

        await flash("Control created", "info")
        return jsonify({"status": "ok", "msg": obj.as_dict()}), 201
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x) }), 500


@bp.route('/api/v1.0/controls/<int:pk>', methods=['GET'])
@login_required
async def get(pk):
    obj = await Control.get_by_id(pk)
    if not obj:
        return jsonify(
            {"status": "error", "msg": f"object with id {pk} not found"}), 404

    return jsonify({"status": "ok", "msg": obj.as_dict()}), 200


@bp.route('/api/v1.0/controls/<int:pk>', methods=['PATCH'])
@login_required
async def patch(pk):
    try:
        jsondata = await request.get_json()
        schema = ControlSchema()
        data = schema.load(jsondata)
        async with lock:
            async with db.connection():
                obj = await Control.get_by_id(pk)
                for k, v in data.items():
                    setattr(obj, k, v)
                await obj.save()

        return jsonify({"status": "ok", "msg": obj.as_dict()}), 200
    except Exception as x:
        logger.warning(str(x))
        return jsonify(
            {"status": "error", "msg": f"object with id {pk} not found"}), 404


@bp.route('/api/v1.0/controls/<int:pk>', methods=['DELETE'])
@login_required
async def delete(pk):
    async with lock:
        async with db.connection():
            try:
                obj = await Control.get_by_id(pk)
                await obj.delete_instance()
                await flash("Control deleted", "info")
            except:
                pass

    return jsonify({
        "status": "ok", "msg": ""}), 200
