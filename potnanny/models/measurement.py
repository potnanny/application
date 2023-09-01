import logging
import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class MeasurementSchema(SafeSchema):
    type = fields.String(allow_none=False)
    value = fields.Float(allow_none=False)
    created = fields.Raw(allow_none=True)
    device_id = fields.Integer(allow_none=False)


class Measurement(Base, CRUDMixin):
    __tablename__ = 'measurements'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    value: Mapped[int]
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'created': self.created.isoformat() + "Z",
            'device_id': self.device_id,
        }
