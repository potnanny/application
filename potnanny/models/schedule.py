import asyncio
import logging
import datetime
import marshmallow
import calendar
from peewee_aio import fields
from potnanny.database import BaseModel
from potnanny.models.schemas.safe import SafeSchema
from potnanny.models.weekday import WeekdayMap
from potnanny.controllers.outlet import switch_device_outlet
from .device import Device


logger = logging.getLogger(__name__)


class ScheduleSchema(SafeSchema):
    name = marshmallow.fields.String(allow_none=False)
    on_time = marshmallow.fields.String(allow_none=False)
    off_time = marshmallow.fields.String(allow_none=False)
    days = marshmallow.fields.Integer(allow_none=False)
    outlet = marshmallow.fields.Integer(allow_none=False)
    device_id = marshmallow.fields.Integer(allow_none=True)


class Schedule(BaseModel):
    id = fields.AutoField()
    name = fields.CharField(48)
    days = fields.IntegerField()
    on_time = fields.TimeField()
    off_time = fields.TimeField()
    outlet = fields.IntegerField()
    created = fields.DateTimeField(default=datetime.datetime.utcnow)
    device = fields.ForeignKeyField(Device,
        on_delete='CASCADE',
        backref='schedules' )

    def __str__(self):
        return f"<Schedule id={self.id}>"

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'days': self.days,
            'on_time': ":".join(str(self.on_time).split(":")[0:2]),
            'off_time': ":".join(str(self.off_time).split(":")[0:2]),
            'outlet': self.outlet,
            'device_id': self.device_id,
            'created': self.created.isoformat() + "Z",
        }

    def runs_now(self,
        now:datetime.datetime = datetime.datetime.now(),
        show_key: bool = True):

        """
        Does this schedule need to run now?
        """

        possible_days = WeekdayMap.weekdays_from_value(self.days)
        dow = calendar.day_name[now.weekday()]
        if dow not in possible_days:
            if show_key:
                return (False, None)
            else:
                return False

        for key in ['on', 'off']:
            label = f"{key}_time"
            if not hasattr(self, label):
                continue

            try:
                hh, mm = str(getattr(self, label)).split(':')[0:2]
                if int(hh) == int(now.hour) and int(mm) == int(now.minute):
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


    async def run(self, now:datetime.datetime = datetime.datetime.now()):
        """
        Run this schedule now
        """

        true, key = self.runs_now(now, True)
        if true is not True:
            return

        logger.debug(f"This schedule runs now! {self}")
        try:
            state = 1
            if (key == 'off'):
                state = 0

            logger.debug("Switching device %d, outlet %d %s" % (
                self.device_id, self.outlet, key.upper()))
            rval = await switch_device_outlet(
                self.device_id, self.outlet, state)
            # sleep a while, and switch it again... just to be sure
            await asyncio.sleep(45)
            rval = await switch_device_outlet(
                self.device_id, self.outlet, state)
        except Exception as x:
            logger.warning(x)

        return
