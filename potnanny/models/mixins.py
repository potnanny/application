import asyncio
import logging
import datetime
import potnanny.database as db
from potnanny.locks import LOCKS
from sqlalchemy.inspection import inspect

logger = logging.getLogger(__name__)

class CRUDMixin(object):
    """
    Adds async CRUD functionality to our base sqlalchemy models
    """

    async def insert(self):
        """insert self into db"""

        async def perform():
            async with db.session() as session:
                session.add(self)
                await session.commit()

        await self._execute(perform)


    async def delete(self):
        """delete self from db"""

        async def perform():
            async with db.session() as session:
                await session.delete(self)
                await session.commit()

        await self._execute(perform)


    async def update(self):
        """update self from db"""

        if hasattr(self, 'modified'):
            self.modified = datetime.datetime.utcnow()

        async def perform():
            async with db.session() as session:
                await session.commit()

        await self._execute(perform)


    async def _execute(self, f):
        """execute the session function"""

        if 'db' in LOCKS and LOCKS['db'] is not None:
            async with LOCKS['db']:
                await f()
        else:
            await f()
