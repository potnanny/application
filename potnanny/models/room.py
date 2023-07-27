import asyncio
import logging
from marshmallow import Schema, fields, EXCLUDE, INCLUDE
from sqlalchemy import (Column, Integer, DateTime, Unicode, UnicodeText,
    ForeignKey, func)
from sqlalchemy.orm import relationship
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class RoomSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    notes = fields.String(allow_none=True)


class Room(Base, CRUDMixin):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128), nullable=False, unique=True)
    notes = Column(UnicodeText, nullable=True, unique=False)
    created = Column(DateTime, server_default=func.now())

    # make relationships compatible with asyncio
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    devices = relationship('Device',
        backref='room',
        cascade='all, delete',
        lazy='subquery')


    def __repr__(self):
        return "<Room(id={}, name={})>".format(self.id, self.name)


    def as_dict(self, explore=True):
        """
        present object as a dict.
        args:
            - explore: (boolean) recursively explore relationships and include
              their data as well
        returns:
            dict
        """

        data = {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
            'created': self.created.isoformat() + "Z",
        }
        if explore:
            try:
                data['devices'] = [i.as_dict() for i in self.devices]
            except:
                pass

        return data
