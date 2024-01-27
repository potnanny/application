import logging
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema


logger = logging.getLogger(__name__)


class RoomSchema(SafeSchema):
    name = marshmallow.fields.String()
    notes = marshmallow.fields.String(allow_none=True)


class Room(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(48)
    notes = fields.TextField(null=True)
    created = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"<Room id={self.id}, name='{self.name}'>"

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
            'created': self.created.isoformat() + "Z",
        }
