import logging
from sqlalchemy import (Column, Integer, DateTime, Unicode, UnicodeText,
    ForeignKey, Boolean, func)
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class Trigger(Base, CRUDMixin):
    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, server_default=func.now())
    message = Column(Unicode(128), nullable=True, unique=False)

    # relationships
    action_id = Column(Integer, ForeignKey('actions.id'))

    def __repr__(self):
        return "<Error(id={}, title={})>".format(self.id, self.title)


    def as_dict(self):
        """
        present object as a dict.
        args:
        returns:
            dict
        """

        data = {
            'id': self.id,
            'message': self.message,
            'created': self.created.isoformat() + "Z",
        }

        return data
