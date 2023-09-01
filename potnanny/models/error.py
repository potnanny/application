import logging
import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class Error(Base, CRUDMixin):
    __tablename__ = 'errors'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    message: Mapped[str]
    severity: Mapped[int]
    acknowledged = Mapped[bool]
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

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
