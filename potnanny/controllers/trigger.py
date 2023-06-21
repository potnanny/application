import asyncio
import datetime
from sqlalchemy.sql.expression import select
from potnanny.models.interface import ObjectInterface, execute_statement
from potnanny.models.trigger import Trigger


async def open_action_triggers(action_id: int, start: datetime.datetime):
    """
    Find any open triggers for an action, since the starting time
    """

    stmt = select(Trigger).filter(
        Trigger.action_id == action_id
    ).filter(
        Trigger.created > start
    )

    results = await execute_statement(stmt)
    rows = results.all()
    if len(rows):
        return True
    else:
        return False


async def new_action_trigger(action_id: int):
    """
    Creat a new trigger for an action
    """

    now = datetime.datetime.utcnow().replace(microsecond=0)
    t = Trigger(
        action_id=action_id,
        created=now,
    )
    await t.insert()
