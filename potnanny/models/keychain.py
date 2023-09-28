import logging
import datetime
from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict


logger = logging.getLogger(__name__)


class KeychainSchema(SafeSchema):
    name = fields.String()
    attributes = fields.Dict(allow_none=True)
    protected = fields.Boolean(allow_none=True)


class Keychain(Base, CRUDMixin):
    __tablename__ = 'keychains'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    attributes: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSONEncodedDict))
    protected: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    __mapper_args__ = {'eager_defaults': True}


    def __repr__(self):
        return "<Keychain({})>".format(self.name)


    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'attributes': self.attributes,
            'protected': self.protected
        }
