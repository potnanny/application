import logging
from sqlalchemy import (Column, Integer, DateTime, Unicode, UnicodeText,
    Boolean, ForeignKey, func)
from marshmallow import Schema, fields, EXCLUDE, INCLUDE
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    password = fields.String(allow_none=True)
    roles = fields.String(allow_none=True)


class User(Base, CRUDMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, unique=True)
    password = Column(Unicode(256), nullable=False, unique=False)
    roles = Column(Unicode(256), nullable=False, unique=False, default='user')
    is_active = Column(Boolean, default=True)
    created = Column(DateTime, server_default=func.now())

    # make relationships compatible with asyncio
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
