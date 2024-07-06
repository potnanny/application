import logging
import asyncio
import datetime
import marshmallow
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema
from potnanny.models.mixins import InterfaceMixin
from potnanny.utils.eval import evaluate
from .ext import JSONField


logger = logging.getLogger(__name__)


class ActionSchema(SafeSchema):
    name = marshmallow.fields.String()
    attributes = marshmallow.fields.Dict(allow_none=True)
    interface = marshmallow.fields.String()


class Action(BaseModel, InterfaceMixin):
    id = fields.AutoField()
    name = fields.CharField(48)
    interface = fields.CharField(64)
    attributes = JSONField(default={})
    created = fields.DateTimeField(default=datetime.datetime.utcnow)


    def __str__(self):
        return f"<Action id={self.id}, name='{self.name}'>"


    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'interface': self.interface,
            'attributes': self.attributes,
            'created': self.created.isoformat() + "Z",
        }


    async def input(self, measurement):
        # if existing acton trigger, we skip and wait for trigger to expire
        existing = await self.has_open_trigger()
        if existing:
            return

        stmt = "{0:0.1f} {1:s} {2:0.1f}".format(
            measurement['value'],
            self.attributes['condition'],
            self.attributes['threshold'])
        truth = evaluate(stmt)
        if not truth:
            return

        try:
            # do things here
            klass = self.interface_class(self.interface)
            inst = klass()
            await inst.input(measurement)

            # finally, we assume we did things with our action interface,
            # and now we should remember that something occurred
            await self.init_trigger()
        except Exception as x:
            logger.warning(x)


    async def has_open_trigger(self):
        now = datetime.datetime.utcnow()
        triggers = await ActionTrigger.select().where(
            ActionTrigger.expires > now,
            ActionTrigger.action_id == self.id
        )

        try:
            return bool(len(list(triggers)))
        except:
            return False


    async def init_trigger(self):
        try:
            now = datetime.datetime.utcnow()
            if 'sleep_minutes' in self.attributes:
                end = now + datetime.timedelta(
                    minutes=int(self.attributes['sleep_minutes']))
            else:
                end = now

            t = await ActionTrigger.create(
                created=now,
                expires=end,
                action_id=self.id
            )
            await t.save()
        except Exception as x:
            logger.warning(x)


class ActionTrigger(BaseModel):
    id = fields.AutoField()
    created = fields.DateTimeField(default=datetime.datetime.utcnow)
    expires = fields.DateTimeField(default=datetime.datetime.utcnow)
    action = fields.ForeignKeyField(Action,
        on_delete='CASCADE',
        backref='triggers')


    def __str__(self):
        return f"<ActionTrigger id={self.id}, expires={self.expires}>"


    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'action_id': self.action_id,
            'created': self.created.isoformat() + "Z",
            'expires': self.expires.isoformat() + "Z",
        }
