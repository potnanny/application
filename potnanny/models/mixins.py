import asyncio
import logging
import datetime
import potnanny.database as db
from typing import Callable, Awaitable
from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio.session import AsyncAttrs
from potnanny.locks import LOCKS


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
        """delete self (really, an instance of self) from db"""

        async def perform():
            klass = self.__class__
            stmt = select(klass).filter(klass.id == self.id)
            async with db.session() as session:
                results = await session.execute(stmt)
                obj = results.scalars().one_or_none()
                if obj:
                    await session.delete(obj)
                    await session.commit()

        await self._execute(perform)


    async def update(self):
        """update the instance of self into the db"""

        if hasattr(self, 'modified'):
            self.modified = datetime.datetime.utcnow()

        async def perform():
            changes = 0
            klass = self.__class__
            stmt = select(klass).filter(klass.id == self.id)
            async with db.session() as session:
                results = await session.execute(stmt)
                obj = results.scalars().one_or_none()
                if obj:
                    for attr in dir(self):
                        try:
                            current = getattr(self, attr)
                        except:
                            continue

                        if (attr.startswith('_') or
                            isinstance(current, Callable) or
                            isinstance(current, Awaitable) or
                            isinstance(current, AsyncAttrs._AsyncAttrGetitem)):
                            continue

                        old_value = getattr(obj, attr)
                        if current != old_value:
                            setattr(obj, attr, current)
                            changes += 1

                if changes:
                    await session.commit()

        await self._execute(perform)


    async def _execute(self, f):
        """execute the session-based function, within the scope of the lock"""

        if 'db' in LOCKS and LOCKS['db'] is not None:
            async with LOCKS['db']:
                await f()
        else:
            await f()
