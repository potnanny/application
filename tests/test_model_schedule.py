import unittest
import datetime
from unittest import IsolatedAsyncioTestCase
from potnanny.database import db
from potnanny.models.schedule import Schedule


DBFILE = '/tmp/test.db'

async def init_tables():
    db.init(f'aiosqlite:///{DBFILE}')
    db.register(Schedule)
    await Schedule.create_table()


class TestModels(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_tables()

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(DBFILE)
        except:
            pass

    async def test_create(self):
        opts = {
            'name': 'test',
            'days': 127,
            'on_time': '06:00',
            'off_time': '07:00',
            'device': 1,
            'outlet': 1
        }
        s = await Schedule.create(**opts)
        await s.save()
        assert s.id > 0


    async def test_runs(self):
        now = datetime.datetime.now().replace(second=0,microsecond=0)
        then = now + datetime.timedelta(minutes=10)

        opts = {
            'name': 'immediate test',
            'days': 127,
            'on_time': f"{now.hour}:{now.minute}",
            'off_time': "00:01",
            'device': 1,
            'outlet': 1
        }

        s = await Schedule.create(**opts)
        await s.save()

        # should always produce True
        true, key = s.runs_now(now, True)
        assert true is True
        assert key == 'on'

        # should produce false
        true, key = s.runs_now(then, True)
        assert true is False


if __name__ == '__main__':
    unittest.main()
