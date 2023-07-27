import re
import asyncio
import logging
import datetime
from sqlalchemy import (Column, Integer, Text, String, Float, Boolean,
    DateTime, ForeignKey, func)
from sqlalchemy.orm import relationship
from potnanny.database import Base
from potnanny.plugins.mixins import InterfaceMixin
from potnanny.controllers.trigger import (open_action_triggers,
    new_action_trigger)
from potnanny.utils import evaluate
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict


logger = logging.getLogger(__name__)


class Action(Base, CRUDMixin, InterfaceMixin):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=False)
    interface = Column(String(128), nullable=True, unique=False)
    created = Column(DateTime, server_default=func.now())
    attributes = Column(MutableDict.as_mutable(JSONEncodedDict), nullable=True)

    # make relationships compatible with asyncio
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    device_id = Column(Integer, ForeignKey('devices.id'))


    def __repr__(self):
        return "<Action ({})>".format(self.name)


    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat() + "Z",
            'device_id': self.device_id,
            'interface': self.interface,
            'attributes': self.attributes,
        }

        return data


    async def _existing_trigger(self):

        try:
            minutes = int(self.attributes['sleep_minutes'])
            now = datetime.datetime.utcnow()
            start = now - datetime.timedelta(minutes=minutes)
            results = await open_action_triggers(self.id, start)
            if results:
                return True
        except:
            pass

        return False


    async def input(self, data):
        """
        Accept measurement data as input, evaluate, and perform actions
        as required:
        args:
            - dict (measurement data from a device)
        returns:
        """

        success = False

        if self._precheck(data) is not True:
            logger.debug(f"data {data} is not acceptable. skipping")
            return

        try:
            equation = "%0.1f %s %s" % (
                float(data['value']),
                self.attributes['condition'],
                self.attributes['threshold'])
            if evaluate(equation) is not True:
                return
        except:
            return

        if await self._existing_trigger():
            logger.debug(f"data {data} has an existing trigger. skipping")
            return

        try:
            klass = self.interface_class(self.interface)
            obj = klass(action_id=self.id, action_name=self.name)
            success = await obj.input(data)
        except Exception as x:
            logger.debug(f"Action interface plugin fail: {x}")
            return

        try:
            if (success and 'sleep_minutes' in self.attributes and
                self.attributes['sleep_minutes'] > 0):
                await new_action_trigger(self.id)
        except Exception as x:
            logger.warning(f"Failed to create action trigger for {self.name}")


    def _precheck(self, data):
        """
        examine incoming data, decide if it is valid for us
        """

        try:
            if data['type'] != self.attributes['type']:
                return False
        except:
            return False

        try:
            if data['device_id'] != self.device_id:
                return False
        except:
            return False

        return True
