import logging
from marshmallow import Schema, fields, EXCLUDE, INCLUDE
from sqlalchemy import (Column, Integer, Unicode, UnicodeText, Float, DateTime,
    ForeignKey, func)
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class MeasurementSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    type = fields.String(allow_none=False)
    value = fields.Float(allow_none=False)
    created = fields.Raw(allow_none=True)
    device_id = fields.Integer(allow_none=False)


class Measurement(Base, CRUDMixin):
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True)
    type = Column(Unicode(24), nullable=False, index=True)
    value = Column(Float, nullable=False)
    created = Column(DateTime, server_default=func.now())

    # make relationships compatible with asyncio
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'created': self.created.isoformat() + "Z",
            'device_id': self.device_id,
        }
