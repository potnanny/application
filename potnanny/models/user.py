import logging
import datetime
import marshmallow
from peewee_aio import fields
from quart_auth import AuthUser
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema


logger = logging.getLogger(__name__)


class UserSchema(SafeSchema):
    name = marshmallow.fields.String()
    password = marshmallow.fields.String(allow_none=True)
    roles = marshmallow.fields.String(allow_none=True)


class User(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(24, unique=True)
    roles = fields.CharField(48, default='user')
    password = fields.CharField(512)
    created = fields.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"<User id={self.id}, name='{self.name}'>"

    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'roles': self.notes,
            'created': self.created.isoformat() + "Z",
        }


class SessionUser(AuthUser):
    def __init__(self, auth_id):
        super().__init__(auth_id)
        self._resolved = False
        self._user = None

    async def _resolve(self):
        if not self._resolved:
            self._user = await User.get_by_id(int(self._auth_id))
            self._resolved = True

    @property
    async def name(self):
        await self._resolve()
        return self._user.name
