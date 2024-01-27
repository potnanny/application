import logging
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.mixins import DeviceMixin
from potnanny.models.schemas.safe import SafeSchema
from .room import Room
from .ext import JSONField


logger = logging.getLogger(__name__)


class DeviceSchema(SafeSchema):
    name = marshmallow.fields.String()
    notes = marshmallow.fields.String(allow_none=True)
    room_id = marshmallow.fields.Integer(allow_none=True)
    interface = marshmallow.fields.String()
    attributes = marshmallow.fields.Dict(allow_none=True)


class Device(BaseModel, DeviceMixin):
    id = fields.AutoField()
    name = fields.CharField(48)
    interface = fields.CharField(64)
    attributes = JSONField(default={})
    created = fields.DateTimeField(default=datetime.datetime.utcnow)
    room = fields.ForeignKeyField(Room,
        null=True,
        on_delete='CASCADE',
        backref='devices')

    def __str__(self):
        return f"<Device id={self.id}, name='{self.name}'>"

    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'interface': self.interface,
            'attributes': self.attributes,
            'created': self.created.isoformat() + "Z",
            'room_id': self.room_id,
        }

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
        except:
            pass

        return data
