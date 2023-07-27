import logging
import datetime
import potnanny.database as db
from sqlalchemy.sql.expression import select
from sqlalchemy import delete
from potnanny.locks import LOCKS


logger = logging.getLogger(__name__)


async def execute_statement(stmt):
    results = None
    try:
        async with db.session() as session:
            results = await session.execute(stmt)
    except Exception as x:
        logger.warning(x)
        pass

    return results


class ObjectInterface:
    """
    Class to query Sqlalchemy object models, on the most common ways to fetch
    them:
        - by id
        - by name
        - all of them
    """

    def __init__(self, target_class):
        self.klass = target_class


    async def get_by_id(self, obj_id:int):
        """
        Get an object by its ID attribute
        """

        stmt = select(self.klass).filter(self.klass.id == obj_id)
        try:
            results = await execute_statement(stmt)
            obj = results.one_or_none()[0]
            logger.debug(f"Object: {obj}")
            return obj
        except:
            return None


    async def get_by_name(self, name:str):
        """
        Get an object by its NAME attribute
        """

        stmt = select(self.klass).filter(self.klass.name == name)
        try:
            results = await execute_statement(stmt)
            obj = results.one_or_none()[0]
            logger.debug(f"Object: {obj}")
            return obj
        except:
            return None


    async def get_all(self):
        """
        Get all objects of the Class
        """

        stmt = select(self.klass)
        try:
            results = await execute_statement(stmt)
            items = [item[0] for item in results.all()]
            return items
        except:
            return []


    async def update(self, pk, data):
        """
        Update data for an object id
        """

        stmt = select(self.klass).filter(self.klass.id == pk)
        obj = None

        async def process(stmt):
            async with db.session() as session:
                changed = 0
                results = await session.execute(stmt)
                obj = results.one_or_none()[0]
                for k, v in data.items():
                    if hasattr(obj, k) and getattr(obj, k) != v:
                        setattr(obj, k, v)
                        changed += 1

                if changed:
                    await session.commit()

        try:
            if 'db' in LOCKS and LOCKS['db'] is not None:
                async with LOCKS['db']:
                    await process(stmt)
            else:
                await process(stmt)

        except Exception as x:
            logger.warning(x)

        return obj


    async def delete(self, pk):
        """
        Delete an object id
        """

        stmt = delete(self.klass).where(self.klass.id == pk)

        async def process(stmt):
            async with db.session() as session:
                results = await session.execute(stmt)
                await session.commit()

        try:
            if 'db' in LOCKS and LOCKS['db'] is not None:
                async with LOCKS['db']:
                    await process(stmt)
            else:
                await process(stmt)

        except Exception as x:
            logger.warning(x)

        return None
