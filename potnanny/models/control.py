import logging
import asyncio
import datetime
import marshmallow
import potnanny.controllers.worker as worker
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.controllers.outlet import switch_device_outlet
from potnanny.models.schemas.safe import SafeSchema
from potnanny.utils.eval import evaluate
from .device import Device
from .ext import JSONField


logger = logging.getLogger(__name__)


class ControlSchema(SafeSchema):
    name = marshmallow.fields.String()
    device_id = marshmallow.fields.Integer()
    outlet = marshmallow.fields.Integer()
    attributes = marshmallow.fields.Dict(allow_none=True)


class Control(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(48)
    outlet = fields.IntegerField()
    attributes = JSONField(default={})
    created = fields.DateTimeField(default=datetime.datetime.utcnow)
    device = fields.ForeignKeyField(Device,
        on_delete='CASCADE',
        backref='controls' )


    def __str__(self):
        return f"<Control id={self.id}, name='{self.name}'>"


    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'outlet': self.outlet,
            'device_id': self.device_id,
            'attributes': self.attributes,
            'created': self.created.isoformat() + "Z",
        }


    async def input(self, data:dict):
        """
        Accept measurement data as input, evaluate, and perform on/off control
        as required:
        """

        if self._precheck(data) is not True:
            return

        states = {'on': 1, 'off': 0}
        for key in ('on', 'off'):
            if (key not in self.attributes or not self.attributes[key] or
                self.attributes[key]['condition'] in [None, "", "null"] or
                self.attributes[key]['threshold'] in [None, "", "null"]):
                continue

            working = self.attributes[key]
            equation = "%0.1f %s %s" % (
                float(data['value']),
                working['condition'],
                working['threshold'])

            try:
                if evaluate(equation) is True:
                    state = states[key]

                    # switch device to state
                    t1 = asyncio.create_task(self.switch_task(
                        self.device_id,
                        self.outlet,
                        state))

                    # timed switch? set back to original state after N seconds...
                    if 'seconds' in working and int(working['seconds']) > 0:
                        t2 = asyncio.create_task(self.switch_task(
                            self.device_id,
                            self.outlet,
                            int(not state),
                            int(working['seconds'])
                        ))
            except Exception as x:
                logger.warning(x)


    def _precheck(self, data:dict) -> bool:
        """
        examine incoming data, decide if it is valid for us
        """

        try:
            if data['device_id'] != self.attributes['input_device_id']:
                return False
        except Exception as x:
            logger.warning(str(x))
            return False

        try:
            if data['type'] != self.attributes['type']:
                return False
        except Exception as x:
            logger.warning(str(x))
            return False

        return True


    async def switch_task(self, device:int, outlet:int, state:int, delay:int = 0):
        try:
            if delay:
                await asyncio.sleep(delay)
                rval = await switch_device_outlet(device, outlet, state)
                return rval
            else:
                rval = await switch_device_outlet(device, outlet, state)
                return rval
        except Exception as x:
            logger.warning(x)

        return -1
