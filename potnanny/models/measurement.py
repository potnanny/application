import logging
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema
from potnanny.utils import utcnow
from .device import Device


logger = logging.getLogger(__name__)


class MeasurementSchema(SafeSchema):
    type = marshmallow.fields.String(allow_none=False)
    value = marshmallow.fields.Float(allow_none=False)
    created = marshmallow.fields.Raw(allow_none=True)
    device_id = marshmallow.fields.Integer(allow_none=False)


class Measurement(BaseModel):
    id = fields.AutoField()
    type = fields.CharField(24)
    value = fields.FloatField()
    created = fields.DateTimeField(default=utcnow)
    device = fields.ForeignKeyField(Device,
        on_delete='CASCADE',
        backref='measurements' )

    def __str__(self):
        return f"<Measurement id={self.id}, type={self.type}, value={self.value}>"

    def as_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'device_id': self.device_id,
            'created': self.created.isoformat() + "Z",
        }
