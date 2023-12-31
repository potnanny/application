import re
import asyncio
import logging
import datetime
from typing import Any
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.controllers.outlet import switch_device_outlet
from potnanny.utils import evaluate
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict


logger = logging.getLogger(__name__)


class ControlSchema(SafeSchema):
    name = fields.String()
    device_id = fields.Integer()
    outlet = fields.Integer()
    attributes = fields.Dict(allow_none=True)


class Control(Base, CRUDMixin):
    __tablename__ = 'controls'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    outlet: Mapped[int]
    attributes: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSONEncodedDict))
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))


    def __repr__(self):
        return "<Control ({})>".format(self.name)


    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat() + "Z",
            'device_id': self.device_id,
            'outlet': self.outlet,
            'attributes': self.attributes,
        }

        return data


    async def input(self, data):
        """
        Accept measurement data as input, evaluate, and perform on/off control
        as required:
        args:
            - dict (measurement data
        returns:
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

            if evaluate(equation) is True:
                state = states[key]

                # switch device to state
                t1 = asyncio.create_task(self.switch_task(
                    self.device_id,
                    self.outlet,
                    state))

                # timed switch? set back to original state after seconds...
                if 'seconds' in working and int(working['seconds']) > 0:
                    t2 = asyncio.create_task(self.switch_task(
                        self.device_id,
                        self.outlet,
                        int(not state),
                        int(working['seconds'])
                    ))


    def _precheck(self, data):
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


    async def switch_task(self, device: int, outlet: int, state: int, delay: int = 0):
        try:
            if delay:
                await asyncio.sleep(delay)
                await switch_device_outlet(device, outlet, state)
            else:
                await switch_device_outlet(device, outlet, state)
        except Exception as x:
            logger.warning(x)
