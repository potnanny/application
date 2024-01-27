import logging
from quart import Blueprint, jsonify, render_template, abort, request
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.database import db


logger = logging.getLogger(__name__)
bp = Blueprint('keychains', __name__, template_folder='templates')


@bp.route('/api/v1.0/keychains', methods=['GET'])
@login_required
async def get_list():
    objects = await Keychain.select()
    if not objects:
        return jsonify({"status": "error", "msg": "object not found"}), 404

    return jsonify({
        "status": "ok", "msg": [o.as_dict()  for o in objects] }), 200


@bp.route('/api/v1.0/keychains', methods=['POST'])
@login_required
async def create():
    jsondata = await request.get_json()
    schema = KeychainSchema()
    data = schema.load(jsondata)
    try:
        async with db.connection():
            obj = Keychain.create(**data)
            await obj.save()

        await flash("Keychain created", "success")
        return jsonify({"status": "ok", "msg": obj.as_dict()}), 201
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x) }), 500


@bp.route('/api/v1.0/keychains/<int:pk>', methods=['GET'])
@login_required
async def get(pk):
    obj = await Keychain.get_by_id(pk)
    if not obj:
        return jsonify(
            {"status": "error", "msg": f"object with id {pk} not found"}), 404

    return jsonify({"status": "ok", "msg": obj.as_dict()}), 200


@bp.route('/api/v1.0/keychains/<int:pk>', methods=['PATCH'])
@login_required
async def patch(pk):
    jsondata = await request.get_json()
    schema = KeychainSchema()
    data = schema.load(jsondata)
    obj = None

    async with db.connection():
        obj = await Keychain.get_by_id(pk)
        if not obj:
            return jsonify(
                {"status": "error", "msg": f"object with id {pk} not found"}), 404
        for k,v in data.items():
            setattr(obj, k, v)
        await obj.save()

    return jsonify({"status": "ok", "msg": obj.as_dict()}), 200


@bp.route('/api/v1.0/keychains/<int:pk>', methods=['DELETE'])
@login_required
async def delete(pk):
    with db.connection():
        try:
            obj = await Keychain.get_by_id(pk)
            await obj.delete_instance()
            await flash("Keychain deleted", "success")
        except:
            pass

    return jsonify({
        "status": "ok", "msg": ""}), 200
