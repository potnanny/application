import logging
from quart import Blueprint, jsonify, render_template, abort
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.models.keychain import Keychain, KeychainSchema
from potnanny.database import db


logger = logging.getLogger(__name__)
bp = Blueprint('settings', __name__, template_folder='templates')


@bp.route('/settings', methods=['GET'])
@login_required
async def index():
    obj = await Keychain.select().where(Keychain.name == 'settings')[0]

    try:
        return await render_template('settings/index.html', title='Settings',
            data=obj.as_dict())
    except TemplateNotFound:
        abort(404)


@bp.route('/api/v1.0/settings', methods=['GET'])
@login_required
async def get():
    try:
        obj = await Keychain.select().where(Keychain.name == 'settings')[0]
        if not obj:
            return jsonify({
                "status": "error", "msg": f"object id {pk} not found"}), 404

        return jsonify({"status": "ok", "msg": obj.as_dict()}), 200
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x)}), 500


@bp.route('/api/v1.0/settings', methods=['PATCH'])
@login_required
async def patch():
    try:
        jsondata = await request.get_json()
        schema = KeychainSchema()
        data = schema.load(jsondata)
        async with db.connection():
            obj = await Keychain.select().where(Keychain.name == 'settings')[0]
            if not obj:
                return jsonify({
                    "status": "error", "msg": f"object id {pk} not found"}), 404

            for k, v in data.items():
                setattr(obj, k, v)
            await obj.save()

        return jsonify({"status": "ok", "msg": obj.as_dict()}), 200
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x)}), 500
