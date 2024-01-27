import logging
from quart import (Blueprint, render_template, redirect, jsonify, request,
    abort, flash)
from quart_auth import login_required
from jinja2 import TemplateNotFound
from potnanny.utils import iso_from_sqlite
from potnanny.models.room import Room, RoomSchema
from potnanny.database import db
from .forms import RoomForm


logger = logging.getLogger(__name__)
bp = Blueprint('rooms', __name__, template_folder='templates')


@bp.route('/rooms/edit', methods=['GET', 'POST'])
@bp.route('/rooms/edit/<int:pk>', methods=['GET', 'POST'])
@login_required
async def room_edit(pk:int = 0):
    if pk:
        obj = await Room.get_by_id(pk)
        if not obj:
            abort(404)
    else:
        obj = {}

    form = await RoomForm.create_form(obj=obj)

    if request.method == 'POST':
        logger.debug(form.__dict__)
        logger.debug(f"form delete value: '{form.remove.data}'")

        if await form.validate_on_submit():
            if pk:
                if form.remove.data == 'true':
                    async with db.connection():
                        await obj.delete_instance()
                    await flash("room deleted", 'info')
                else:
                    obj.name = form.name.data
                    obj.notes = form.notes.data
                    await obj.save()
                    await flash("room updated", 'info')
            else:
                room = await Room.create(
                    name=form.name.data,
                    notes=form.notes.data)
                await room.save()
                await flash(f"room '{room.name}' created", 'info')
            return redirect("/")

    try:
        return await render_template('rooms/form.html', form=form)
    except TemplateNotFound:
        abort(404)



@bp.route('/api/v1.0/rooms', methods=['GET'])
@login_required
async def get_list():
    objects = await Room.select()
    if not objects:
        return jsonify({"status": "error", "msg": "no data"}), 404

    payload = [o.as_dict() for o in objects]
    return jsonify({"status": "ok", "msg": payload}), 200


@bp.route('/api/v1.0/rooms', methods=['POST'])
@login_required
async def create():
    try:
        jsondata = await request.get_json()
        schema = RoomSchema()
        data = schema.load(jsondata)
        async with db.connection():
            obj = await Room.create(**data)
            await obj.save()

        await flash("Room created", "info")
        return jsonify({"status": "ok", "msg": obj.as_dict()}), 201
    except Exception as x:
        return jsonify({"status": "error", "msg": str(x)}), 500


@bp.route('/api/v1.0/rooms/<int:pk>', methods=['GET'])
@login_required
async def get(pk):
    payload = None
    obj = await Room.get_by_id(pk)
    if obj is None:
        return jsonify({
            "status": "error", "msg": f"object id {pk} not found"}), 404

    return jsonify({"status": "ok", "msg": obj.as_dict()}), 200


@bp.route('/api/v1.0/rooms/<int:pk>', methods=['PATCH'])
@login_required
async def patch(pk):
    try:
        logger.debug(request.__dict__)
        jsondata = await request.get_json()
        logger.debug(jsondata)
        schema = RoomSchema()
        data = schema.load(jsondata)
        async with db.connection():
            obj = await Room.get_by_id(pk)
            if not obj:
                return jsonify({
                    "status": "error", "msg": f"object id {pk} not found"}), 404
            for k, v in data.items():
                setattr(obj, k, v)
            await obj.save()

        return jsonify({"status": "ok", "msg": obj.as_dict()}), 200
    except Exception as x:
        logger.warning(x)
        return jsonify({"status": "error", "msg": str(x)}), 500


@bp.route('/api/v1.0/rooms/<int:pk>', methods=['DELETE'])
@login_required
async def delete(pk):
    async with db.connection():
        try:
            obj = await Room.get_by_id(pk)
            await obj.delete_instance()
            await flash("Room deleted", "info")
        except:
            pass

    return jsonify({"status": "ok", "msg": ""}), 202
