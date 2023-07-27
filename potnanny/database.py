import os
import logging
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncSession,
    AsyncAttrs)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from potnanny.utils import hash_password


engine = None
session = None
logger = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def init_db(uri, **kwargs):
    """
    Create db engine, sessionmaker, and tables.
    args:
        - uri, str
    returns:
    """

    if not engine:
        await init_engine(uri, **kwargs)

    if not session:
        await init_sessionmaker(engine)

    await init_tables()


async def init_engine(uri, **kwargs):
    """
    Init the engine.

    args:
        - uri, sqlalchemy engine db uri init string
        - optional keyword args to pass to sqlalchemy create_async_engine func
    returns:
    """

    global engine
    logger.debug(f"Initializing db engine {uri}")
    engine = create_async_engine(uri, **kwargs)


async def init_sessionmaker(engine=engine):
    """
    Init the sessionmaker function with the engine.

    args:
        - an engine instance
    returns:
    """

    global session
    logger.debug("Initializing db session")
    session = sessionmaker(engine,
        expire_on_commit=False, class_=AsyncSession)


async def init_tables():
    """
    Create tables based on sqlalchemy models.

    args:
    returns:
    """

    logger.debug("Importing models")

    # import the  models
    from potnanny.models.keychain import Keychain
    from potnanny.models.user import User
    from potnanny.models.room import Room
    from potnanny.models.device import Device
    from potnanny.models.measurement import Measurement
    from potnanny.models.control import Control
    from potnanny.models.schedule import Schedule
    from potnanny.models.error import Error
    from potnanny.models.action import Action
    from potnanny.models.trigger import Trigger

    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # create initial default config
    try:
        attrs = {
            'temperature_display': 'F',
            'polling_interval': 10,
            'plugin_path': os.path.expanduser('~/potnanny/plugins'),
            'leaf_offset': -2,
            'storage_days': 5,
        }
        kc = Keychain(name='settings', attributes=attrs, protected=True)
        await kc.insert()
    except:
        pass

    # create the default admin user
    try:
        attrs = {
            'name': 'admin',
            'roles': 'admin,user',
            'password': hash_password('potnanny!'),
        }
        user = User(**attrs)
        await user.insert()
    except:
        pass

    try:
        opts = {
            'name': 'features',
            'protected': True,
            'attributes': {
                'room_limit': 1,
                'device_limit': 4
            }
        }
        kc = Keychain(**opts)
        await kc.insert()
    except:
        pass
