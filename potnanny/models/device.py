import logging
import datetime
from typing import List, Optional, Any
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.plugins.mixins import PluginMixin
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict


logger = logging.getLogger(__name__)


class DeviceSchema(SafeSchema):
    name = fields.String()
    notes = fields.String(allow_none=True)
    room_id = fields.Integer(allow_none=True)
    interface = fields.String()
    attributes = fields.Dict(allow_none=True)


class Device(Base, CRUDMixin, PluginMixin):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    interface: Mapped[Optional[str]]
    attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(MutableDict.as_mutable(JSONEncodedDict))
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    measurements: Mapped[List['Measurement']] = relationship(
        backref='device',
        cascade='all,delete',
        lazy='subquery')
    schedules: Mapped[List['Schedule']] = relationship(
        backref='device',
        cascade='all,delete',
        lazy='subquery')
    controls: Mapped[List['Control']] = relationship(
        backref='device',
        cascade='all,delete',
        lazy='subquery')


    def __repr__(self):
        return "<Device ({})>".format(self.name)

    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'created': self.created.isoformat() + "Z",
            'room_id': self.room_id,
            'interface': self.interface,
            'attributes': self.attributes,
        }

        try:
            data['controls'] = [c.as_dict() for c in self.controls]
        except:
            pass

        try:
            data['schedules'] = [s.as_dict for s in self.schedules]
        except:
            pass

        try:
            mylist = self.plugin.reports
            if ('temperature' in mylist and
                'humidity' in mylist and 'vpd' not in mylist):
                mylist.append('vpd')
            data['reports'] = mylist
        except:
            pass

        try:
            for k, v in self.plugin.__dict__.items():
                if 'plugin' not in data:
                    data['plugin'] = {}

                if k.startswith('_'):
                    continue

                data['plugin'][k] = v
        except Exception as x:
            logger.debug(x)

        return data


    async def poll(self):
        """
        Poll our plugin instance for measurements, if possible
        args:
            none
        returns:
            dict, or None
        """

        if (not hasattr(self.plugin, 'is_pollable') or
            self.plugin.is_pollable is not True):
            return None

        results = {
            'id': self.id,
            'name': self.name,
            'values': {},
        }

        try:
            logger.debug("polling plugin instance: %s" % self.plugin)
            values = await self.plugin.poll()
            results['values'] = values
        except Exception as x:
            logger.warning(str(x))

        return results


    def read_advertisement(self, device, advertisement):
        """
        Use plugin instance to decode the BLE advertisement data
        args:
            the device reporting data
            the advertisement data
        returns:
            dict, or None
        """

        if (not hasattr(self.plugin, 'is_reader') or
            self.plugin.is_reader is not True):
            return None

        results = {
            'id': self.id,
            'name': self.name,
            'values': {},
        }

        try:
            values = self.plugin.read_advertisement(device, advertisement)
            if values:
                results['values'] = values
        except:
            pass

        return results


    async def on(self, outlet=1):
        """
        Switch device ON
        """

        if (not hasattr(self.plugin, 'is_switchable') or
            self.plugin.is_switchable is not True):
            return None

        try:
            result = await self.plugin.on(outlet)
            return result
        except Exception as x:
            logger.warning(str(x))
            return None


    async def off(self, outlet=1):
        """
        Switch device OFF
        """

        if (not hasattr(self.plugin, 'is_switchable') or
            self.plugin.is_switchable is not True):
            return None

        try:
            result = await self.plugin.off(outlet)
            return result
        except Exception as x:
            logger.warning(str(x))
            return None


    async def set_value(self, data):
        """
        *FUTURE*
        Set key/value data on device.
        args:
            - dict
        returns:
        """

        if (not hasattr(self.plugin, 'is_settable') or
            self.plugin.is_settable is not True):
            return None

        if type(data) is not dict:
            logger.warning("Expecting dict but got %s" % type(data))
            return None

        try:
            result = await self.plugin.set_value(data)
            return result
        except Exception as x:
            logger.warning(x)
            return None
