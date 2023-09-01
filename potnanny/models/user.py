import logging
import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class UserSchema(SafeSchema):
    name = fields.String()
    password = fields.String(allow_none=True)
    roles = fields.String(allow_none=True)


class User(Base, CRUDMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    roles: Mapped[str] = mapped_column(default='user')
    is_active: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}


    def __repr__(self):
        return "<User(id={}, name={})>".format(self.id, self.name)


    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'roles': self.roles,
            'created': self.created.isoformat() + "Z",
            'is_active': self.is_active,
        }


    def has_role(self, role):
        if role in self.roles.split(','):
            return True

        return False


    def add_role(self, role):
        if not self.has_role(role):
            if self.roles is None:
                self.roles = role
            else:
                self.roles += ",%s" % role


    def remove_role(self, role):
        atoms = self.roles.split(',')
        try:
            atoms.remove(role)
        except:
            pass

        self.roles = ",".join(atoms)
