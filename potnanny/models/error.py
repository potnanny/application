import logging
from sqlalchemy import (Column, Integer, DateTime, Unicode, UnicodeText,
    ForeignKey, Boolean, func)
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class Error(Base, CRUDMixin):
    __tablename__ = 'errors'

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(64), nullable=False, unique=False)
    message = Column(UnicodeText, nullable=False, unique=False)
    severity = Column(Integer, nullable=False, unique=False, default=1)
    acknowledged = Column(Boolean, nullable=False, unique=False, default=False)
    created = Column(DateTime, server_default=func.now())

    # severity = 1: minor, 2: major, 3: critical

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
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'acknowledged': self.acknowledged,
            'created': self.created.isoformat() + "Z",
        }

        return data
