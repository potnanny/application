import logging
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema
from .ext import JSONField


logger = logging.getLogger(__name__)


class LicenseSchema(SafeSchema):
    name = marshmallow.fields.String()
    description = marshmallow.fields.String()
    attributes = marshmallow.fields.Dict(allow_none=True)


class License(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(48, unique=True)
    description = fields.CharField(128, unique=False)
    attributes = JSONField(default={})
    created = fields.DateField(default=datetime.date.today)

    def __str__(self):
        return f"<License id={self.id}, name='{self.name}'>"

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'attributes': self.attributes,
            'created': self.created.isoformat() + "Z",
        }
