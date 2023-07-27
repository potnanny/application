from aiohttp import web
from potnanny.models.keychain import Keychain
from potnanny.models.interface import ObjectInterface
from marshmallow import Schema, fields, validate, EXCLUDE
from .decorators import login_required

routes = web.RouteTableDef()

class SettingSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    temperature_display = fields.String(allow_none=True,
        validate=validate.OneOf(['f','F','c','C']))
    polling_interval = fields.Integer(allow_none=True,
        validate=validate.Range(min=1,max=30))
    plugin_path = fields.String(allow_none=True)
    leaf_offset = fields.Integer(allow_none=True,
        validate=validate.Range(min=-5,max=5))
    storage_days = fields.Integer(allow_none=True,
        validate=validate.Range(min=1,max=365))


@routes.get('/api/v1.0/settings')
@login_required
async def get(request):
    obj = await ObjectInterface(Keychain).get_by_name('settings')
    if not obj:
        return web.json_response({
            "status": "error", "msg": "settings object not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": obj.as_dict() }, status=200)


@routes.patch('/api/v1.0/settings')
@login_required
async def patch(request):
    jsondata = await request.json()
    schema = SettingSchema()
    data = schema.load(jsondata['attributes'])
    obj = await ObjectInterface(Keychain).get_by_name('settings')
    if not obj:
        return web.json_response({
            "status": "error", "msg": "settings object not found"},
            status=404)

    pk = obj.id
    shiny = await ObjectInterface(Keychain).update(pk, data)
    if not shiny:
        return web.json_response({
            "status": "error", "msg": "settings object not found"},
            status=404)

    return web.json_response({
        "status": "ok", "msg": shiny.as_dict()}, status=200)
