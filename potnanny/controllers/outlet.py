import asyncio
import datetime
import logging
import random
from sqlalchemy import func
from sqlalchemy.sql.expression import select
from potnanny.models.measurement import Measurement
from potnanny.models.device import Device
from potnanny.models.interface import ObjectInterface, execute_statement
from potnanny.controllers.poll import Poller
from potnanny.locks import LOCKS


logger = logging.getLogger(__name__)


async def switch_device_outlet(device_id: int, outlet_id: int, state: int):
    """
    Convenience function for times when we need a basic function
    like... a functools.partial call
    """

    ctl = OutletControl(device_id, outlet_id)
    result = await ctl.switch(state)
    return result


class OutletControl:
    """
    Class to interface with device switchable outlets
    """

    def __init__(self, device_id: int, outlet_id: int):
        self.device_id = device_id
        self.outlet_id = outlet_id
        self.lock = LOCKS['bluetooth']
        self.device = None


    async def switch(self, state: int, force: bool = False) -> int:
        """
        Switch device to requested state
        """

        if not force:
            latest = await self.last_state()
            if latest == state:
                return state

        success = False
        tries = 3
        while success is not True and tries:
            try:
                if self.lock:
                    async with self.lock:
                        success = await self._switch_outlet(state)
                else:
                    success = await self._switch_outlet(state)

                if success:
                    break
            except:
                pass

            tries -= 1
            await asyncio.sleep(float("%0.1f" % random.random()))

        if not success:
            logger.warning(
                f"Switch fail device {self.device_id}, outlet {self.outlet_id}"
            )
            return -1
        else:
            # use the poller to record the new state of the outlet
            now = datetime.datetime.utcnow().replace(microsecond=0)
            p = Poller(now=now)
            t1 = asyncio.create_task(p.poll_id(self.device_id))
            # result = await self._record_state(state)
            # if not result:
            #    logger.warning("Failed to record outlet switched state")

            return state


    async def last_state(self, threshold: int = 30) -> int:
        """
        Get most recent recorded db measurement of outlet state
        return will be the last state (0|1), or -1 if could not be found.
        """

        now = datetime.datetime.utcnow().replace(microsecond=0)
        start = now - datetime.timedelta(seconds=threshold)

        stmt = select(
            Measurement.value, func.max(Measurement.created)
        ).filter(
            Measurement.device_id == self.device_id
        ).filter(
            Measurement.type == f"outlet_{self.outlet_id}"
        ).group_by(
            Measurement.device_id
        )

        try:
            results = await execute_statement(stmt)
            row = results.first()
            # exclude the record if it older than threshold seconds
            if row[1] < start:
                return -1
            return int(row[0])
        except:
            return -1


    async def _record_state(self, state: int) -> bool:
        """
        Record the new device outlet state in the measurement table
        """

        now = datetime.datetime.utcnow().replace(microsecond=0)
        opts = {
            'device_id': self.device_id,
            'type': f"outlet_{self.outlet_id}",
            'value': state,
            'created': now }

        try:
            meas = Measurement(**opts)
            await meas.insert()
            return True
        except:
            return False


    async def _switch_outlet(self, state):
        if self.device is None:
            try:
                self.device = await ObjectInterface(Device).get_by_id(
                    self.device_id)
            except:
                logger.warning(f"No suitable device found (id {self.device_id})")
                return False

        if not hasattr(self.device.plugin, 'is_switchable') or \
            self.device.plugin.is_switchable is not True:
            logger.warning(f"Device with id {device_id} is not switchable")
            return False

        if bool(state):
            rval = await self.device.on(self.outlet_id)
            if int(rval) == 1:
                return True
        else:
            rval = await self.device.off(self.outlet_id)
            if int(rval) == 0:
                return True

        return False
