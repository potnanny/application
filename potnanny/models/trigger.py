import logging
import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin


logger = logging.getLogger(__name__)


class Trigger(Base, CRUDMixin):
    __tablename__ = 'triggers'

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"))

    def __repr__(self):
        return "<Trigger(id={}, message={})>".format(self.id, self.message)


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
