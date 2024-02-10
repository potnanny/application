import os
import asyncio
import logging
import peewee
from peewee_aio import Manager, AIOModel, fields
from peewee_aio.databases import get_db
from peewee import DatabaseProxy, logger
from weakref import WeakSet
from potnanny.utils.password import hash_password, verify_password


# lock used for db inserts
lock = asyncio.Lock()
logger = logging.getLogger(__name__)


class Database(Manager):
    def __init__(self):
        self.url = None
        self.backend_options = {}
        self.pw_database = DatabaseProxy()

    def init(self, url:str, **backend_options):
        if not url and not self.url:
            raise ValueError("DB url was never given!")
        backend_options.setdefault("convert_params", True)
        self.backend_options.update(backend_options)
        super(Manager, self).__init__(url or self.url, logger=logger,
			**self.backend_options)

        self.models = WeakSet()
        self.pw_database.initialize(get_db(self))


db = Database()


class BaseModel(AIOModel):
    __rel__: {}
    _manager = db

    class Meta:
        database = db.pw_database


async def init_db(url:str, **kwargs):
	db.init(url, **kwargs)
	await init_tables()


async def init_tables():
    from .models.room import Room
    from .models.device import Device
    from .models.measurement import Measurement
    from .models.keychain import Keychain
    from .models.control import Control
    from .models.license import License
    from .models.user import User

    db.register(Room)
    db.register(Device)
    db.register(Measurement)
    db.register(Keychain)
    db.register(Control)
    db.register(License)
    db.register(User)

    async with db.connection():
        await Room.create_table()
        await Device.create_table()
        await Measurement.create_table()
        await Keychain.create_table()
        await Control.create_table()
        await User.create_table()
        await License.create_table()

        try:
            # create default settings
            s_opts = {
                'name': 'settings',
                'protected': True,
                'attributes': {
                    'temperature_display': 'F',
                    'polling_interval': 10,
                    'plugin_path': os.path.expanduser('~/potnanny/plugins'),
                    'leaf_offset': -2,
                    'storage_days': 7,
                    'graph_hours': 24,
                }
            }
            obj = await Keychain.create(**s_opts)
            await obj.save()
        except:
            pass

        try:
            # create default features
            f_opts = {
                'name': 'features',
                'protected': True,
                'attributes': {
                    'room_limit': 1,
                    'device_limit': 4,
                }
            }
            obj = await Keychain.create(**f_opts)
            await obj.save()
        except:
            pass

        try:
            # create default user
            u_opts = {
                'name': 'admin',
                'password': hash_password('potnanny!'),
                'protected': True,
                'roles': "user,admin"
            }
            u = await User.create(**u_opts)
            await u.save()
        except:
            pass
