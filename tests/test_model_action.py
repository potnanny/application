import asyncio
import aiosmtplib
import unittest
import datetime
import potnanny.database as db
from email.mime.text import MIMEText
from unittest import IsolatedAsyncioTestCase
from potnanny.models.room import Room
from potnanny.models.device import Device
from potnanny.models.measurement import Measurement
from potnanny.models.action import Action
from potnanny.models.error import Error
from potnanny.models.trigger import Trigger
from potnanny.models.keychain import Keychain
from potnanny.models.interface import ObjectInterface
from potnanny.plugins import ActionPlugin
from potnanny.controllers.pipeline import Pipeline
from potnanny.plugins import PipelinePlugin



class ActionPipeline(PipelinePlugin):
    """
    Class to route pipeline measurements to controls
    """

    name = "Action Pipeline Plugin"
    description = "Route measurements to Actions"

    def __init__(self, *args, **kwargs):
        pass


    async def input(self, measurements):
        tasks = []
        objects = await ObjectInterface(Action).get_all()
        for obj in objects:
            for m in measurements:

                # pre-filter, only appropriate measurements go to the action
                try:
                    if obj.device_id != m['device_id']:
                        continue

                    if obj.attributes['type'] != m['type']:
                        continue

                    tasks.append(obj.input(m))
                except Exception as x:
                    print(x)

        if not len(tasks):
            return

        try:
            await asyncio.gather(*tasks)
        except Exception as x:
            print(x)




class TestActionModel(IsolatedAsyncioTestCase):
# ###############################################

    async def asyncSetUp(self):
        uri = 'sqlite+aiosqlite://'
        await db.init_db(uri)
        try:
            room = Room(name="test room")
            await room.insert()

            device = Device(
                name="test device",
                interface="Foo",
                room_id=1)
            await device.insert()

            action1 = Action(
                name="test action 1",
                interface="__main__.GmailSender",
                device_id=1,
                attributes={
                    "type": "temperature",
                    "condition": "gt",
                    "threshold": 80
                }
            )
            await action1.insert()

            action2 = Action(
                name="test action 2",
                interface="__main__.GmailSender",
                device_id=1,
                attributes={
                    "type": "humidity",
                    "condition": "gt",
                    "threshold": 50,
                    "sleep_minutes": 60
                }
            )
            await action2.insert()

            now = datetime.datetime.utcnow()
            then = now - datetime.timedelta(minutes=30)
            trigger = Trigger(action_id=2, created=then)
            await trigger.insert()

        except:
            pass


    async def asyncTearDown(self):
        pass

    async def test_create(self):
        measurements = [
            {"type": "humidity", "value": 55.0, "device_id": 1},
            {"type": "battery", "value": 100.0, "device_id": 1},
            {"type": "vpd", "value": 1.0, "device_id": 1},
            {"type": "temperature", "value": 75.0, "device_id": 1},
            {"type": "temperature", "value": 85.0, "device_id": 1},
        ]
        p = Pipeline()
        await p.input(measurements)

if __name__ == '__main__':
    unittest.main()
