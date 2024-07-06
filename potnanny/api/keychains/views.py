import re
import logging
from quart import Blueprint, jsonify, render_template, abort, request
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.database import db
from potnanny.utils.crypt import encrypt_str


logger = logging.getLogger(__name__)
bp = Blueprint('keychains', __name__, template_folder='templates')


@bp.route('/keychains', methods=['GET'])
@login_required
async def get_view():
    objects = await Keychain.select().where(Keychain.protected == False)
    try:
        return await render_template('keychains/index.html',
            data=[o for o in objects])
    except TemplateNotFound:
        abort(404)


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
        if 'password' in data['attributes']:
            # does this look already encrypted?
            if not re.search(r'^g.+=$', data['attributes']['password']):
                pw = encrypt_str(data['attributes']['password'])
                data['attributes']['password'] = pw
    except:
        pass

    try:
        async with db.connection():
            obj = await Keychain.create(**data)
            await obj.save()

        await flash("Keychain created", "info")
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

    try:
        if 'password' in data['attributes']:
            # does this look already encrypted?
            if not re.search(r'^g.+=$', data['attributes']['password']):
                pw = encrypt_str(data['attributes']['password'])
                data['attributes']['password'] = pw
    except:
        pass

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
    async with db.connection():
        try:
            obj = await Keychain.get_by_id(pk)
            if obj.protected == True:
                return jsonify({
                    "status": "error", "msg": "forbidden"}), 403

            await obj.delete_instance()
            await flash("Keychain deleted", "success")
        except:
            pass

    return jsonify({
        "status": "ok", "msg": ""}), 200
