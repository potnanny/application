import asyncio
import logging
import datetime
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class RoomSchema(SafeSchema):
    name = fields.String()
    notes = fields.String(allow_none=True)


class Room(Base, CRUDMixin):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    notes: Mapped[Optional[str]]
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    devices: Mapped[List['Device']] = relationship(
        backref='room',
        cascade='all,delete',
        lazy='subquery')

    def __repr__(self):
        return f"<Room(id={self.id}, name={self.name})>"

    def as_dict(self):
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
        try:
            data['devices'] = [d.as_dict() for d in self.devices]
        except:
            pass

        return data
