import re
import logging
import calendar
import datetime
from typing import Any
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from marshmallow import fields
from potnanny.models.schemas.safe import SafeSchema
from potnanny.utils import utcnow
from potnanny.database import Base
from potnanny.models.mixins import CRUDMixin
from potnanny.models.ext import MutableDict, JSONEncodedDict
from potnanny.models.weekday import WeekdayMap
from potnanny.controllers.outlet import switch_device_outlet


logger = logging.getLogger(__name__)


class ScheduleSchema(SafeSchema):
    name = fields.String(allow_none=False)
    device_id = fields.Integer(allow_none=True)
    outlet = fields.Integer(allow_none=False)
    on_time = fields.String(allow_none=False)
    off_time = fields.String(allow_none=False)
    days = fields.Integer(allow_none=False)


class Schedule(Base, CRUDMixin):
    """
    Time is like: "13:30" (24h/UTC based)
    Days is an INT, based on:
     sunday=64, mon=32, tue=16, wed=8, thu=4, fri=2, sat=1
    """

    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    outlet: Mapped[int]
    days: Mapped[int]
    on_time: Mapped[str]
    off_time: Mapped[str]
    created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    # make relationships compatible with asyncio sessions
    __mapper_args__ = {"eager_defaults": True}

    # relationships
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))


    def __repr__(self):
        return "<Schedule ({}, {}, {})>".format(self.id, self.on_time, self.off_time)


    def as_dict(self):
        return {
            'id': self.id,
            'days': self.days,
            'on_time': self.on_time,
            'off_time': self.off_time,
            'outlet': self.outlet,
            'device_id': self.device_id,
            'created': self.created.isoformat() + "Z",
        }


    def runs_now(self, now=None, show_key=False):
        """
        Does this schedule need to run now? True|False
        """

        if now is None or type(now) is not datetime.datetime:
            now = datetime.datetime.now()

        dow = calendar.day_name[now.weekday()]
        if dow not in WeekdayMap.weekdays_from_value(self.days):
            return False

        for key in ['on', 'off']:
            label = "%s_time" % key
            if not hasattr(self, label):
                continue

            try:
                hh, mm = getattr(self, label).split(':')
                if int(hh) == now.hour and int(mm) == now.minute:
                    if show_key is True:
                        return (True, key)
                    else:
                        return True
            except Exception as x:
                logger.warning(x)

        if show_key is True:
            return (False, None)
        else:
            return False


    async def run(self, now=None):
        """
        Run this schedule now
        """

        if now is None or type(now) is not datetime.datetime:
            # schedule times are stored according to user local time,
            # so we cannot use UTC here. This... shoud be normalized someday,
            # but its a pain in the ass otherwise.
            now = datetime.datetime.now()

        true, key = self.runs_now(now, True)
        if not true:
            return

        try:
            state = 1
            if (key == 'off'):
                state = 0

            logger.debug("Switching device %d, outlet %d %s" % (
                self.device_id, self.outlet, key.upper()))
            rval = await switch_device_outlet(
                self.device_id, self.outlet, state)
        except Exception as x:
            logger.warning(x)

        return
