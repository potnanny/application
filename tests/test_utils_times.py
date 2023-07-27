import os
import unittest
import datetime
from potnanny.utils.times import (utcnow, datetime_from_iso, 
    datetime_from_sqlite, iso_from_sqlite)


class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_utcnow(self):
        dt = utcnow()
        assert type(dt) == datetime.datetime

    def test_conversion(self):
        dt = datetime_from_iso("1970-01-01T00:00:00")
        assert type(dt) == datetime.datetime

    def test_sqlite(self):
        d = '2021-03-14 00:24:41.123'
        dt = datetime_from_sqlite(d)
        assert type(dt) == datetime.datetime

    def test_sqlite_iso(self):
        d = '2021-03-14 00:24:41.123'
        iso = iso_from_sqlite(d)
        assert iso == '2021-03-14T00:24:41.123000Z'

if __name__ == '__main__':
    unittest.main()
