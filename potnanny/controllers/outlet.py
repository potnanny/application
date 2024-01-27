import asyncio
import datetime
import logging
import random
from peewee import fn
from potnanny.database import db
from potnanny.database import lock as db_lock
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.ble import lock as ble_lock


logger = logging.getLogger(__name__)


class OutletControl:
    """
    Class to interface with device switchable outlets
    """

    def __init__(self, device_id: int, outlet_id: int):
        self.device_id = device_id
        self.outlet_id = outlet_id
        self.retries = 5
        self.device = None


    async def switch(self, state: int, force: bool = False) -> int:
        """
        Switch device to requested state
        returns:
            0   = outlet is now off
            1   = outlet is now on
           -1   = outlet was not changed (maybe error, maybe is already in
                  the requested state)
        """

        if not force:
            latest = await self.last_state()
            if latest == state:
                return state

        success = False
        tries = self.retries

        while success is not True and tries:
            try:
                async with ble_lock:
                    success = await self._switch_outlet(state)

                if success:
                    break
            except Exception as x:
                logger.warning(str(x))
                pass

            tries -= 1
            await asyncio.sleep(random.random())

        if success:
            return state
        else:
            logger.warning(
                f"Switch fail device {self.device_id}, outlet {self.outlet_id}"
            )
            return -1


    async def last_state(self, timeout: int = 600) -> int:
        """
        Get most recent recorded db measurement of outlet state
        return will be the last state (0|1), or -1 if could not be found.
        """

        now = datetime.datetime.utcnow().replace(microsecond=0)
        start = now - datetime.timedelta(seconds=timeout)

        try:
            results = await Measurement.select(
                Measurement.id,
                Measurement.type,
                Measurement.value,
                Measurement.device_id,
                fn.MAX(Measurement.created)
            ).where(
                Measurement.device_id == self.device_id,
                Measurement.type == f"outlet_{self.outlet_id}"
            ).group_by(
                Measurement.device_id
            )
            m = results[0]
            if m.created < start:
                return -1
            return int(m.value)
        except Exception as x:
            logger.warning(str(x))

        return -1


    async def _switch_outlet(self, state):
        if self.device is None:
            self.device = await Device.get_by_id(self.device_id)

        if not hasattr(self.device.plugin, 'is_switchable') or \
            self.device.plugin.is_switchable is not True:
            logger.warning(f"Device with id {device_id} is not switchable")
            return False

        logger.debug("switching device...")
        if bool(state):
            rval = await self.device.on(self.outlet_id)
            logger.debug(f"switch rval: {rval}")
            if int(rval) == 1:
                return True
        else:
            rval = await self.device.off(self.outlet_id)
            logger.debug(f"switch rval: {rval}")
            if int(rval) == 0:
                return True

        return False


async def switch_device_outlet(device_id:int, outlet_id:int, state:int):
    """
    Convenience function for times when we need a basic function
    like... a functools.partial call
    """

    ctl = OutletControl(device_id, outlet_id)
    result = await ctl.switch(state, True)
    if result == state:
        async with db_lock:
            async with db.transaction():
                try:
                    m = await Measurement.create(
                        created=datetime.datetime.utcnow().replace(microsecond=0),
                        type=f"outlet_{outlet_id}",
                        value=state,
                        device_id=device_id
                    )
                except Exception as x:
                    logger.warning(str(x))

    return result
