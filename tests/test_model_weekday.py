import unittest
import datetime
import calendar
from unittest import IsolatedAsyncioTestCase
from potnanny.models.weekday import WeekdayMap


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass

    async def test_lookup(self):
        now:datetime.datetime = datetime.datetime.now()
        dow = calendar.day_name[now.weekday()]


if __name__ == '__main__':
    unittest.main()
