import logging
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema
from .ext import JSONField


logger = logging.getLogger(__name__)


class KeychainSchema(SafeSchema):
    name = marshmallow.fields.String()
    attributes = marshmallow.fields.Dict(allow_none=True)
    protected = marshmallow.fields.Boolean(allow_none=True)


class Keychain(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(48, unique=True)
    attributes = JSONField(default={})
    protected = fields.BooleanField(default=False)
    created = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"<Keychain id={self.id}, name='{self.name}'>"

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'attributes': self.attributes,
            'protected': self.protected,
            'created': self.created.isoformat() + "Z",
        }
