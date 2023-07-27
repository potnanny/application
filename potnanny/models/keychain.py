import logging
from marshmallow import Schema, fields, EXCLUDE, INCLUDE
from sqlalchemy import (Column, Integer, String, Float, DateTime,
    ForeignKey, PickleType, Text, Boolean, func)
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict


logger = logging.getLogger(__name__)


class KeychainSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    attributes = fields.Dict(allow_none=True)
    protected = fields.Boolean(allow_none=True)


class Keychain(Base, CRUDMixin):
    """Store named info in a key-value pair."""

    __tablename__ = 'keychains'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    attributes = Column(MutableDict.as_mutable(JSONEncodedDict), nullable=False)
    protected = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, server_default=func.now())

    __mapper_args__ = {'eager_defaults': True}


    def __repr__(self):
        return "<Keychain({})>".format(self.name)


    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'attributes': self.attributes,
            'protected': self.protected }
        return data
