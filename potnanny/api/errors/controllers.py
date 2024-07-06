import logging
import aiofiles
import datetime


logger = logging.getLogger(__name__)


async def get_error_list(path:str, hours:int = 24, reverse:bool = True) -> list:
    """
    Get errors for the last N hours, from a named logfile
    """

    errors = []
    now = datetime.datetime.now()
    try:
        async with aiofiles.open(path, mode='r') as f:
            async for line in f:
                atoms = line.strip().split('|')
                if len(atoms) < 4:
                    continue

                if atoms[2] in ['INFO', 'DEBUG']:
                    continue

                dt = datetime.datetime.strptime(atoms[0], '%Y-%m-%d %H:%M:%S')
                if dt < now - datetime.timedelta(hours=hours):
                    continue

                errors.append({
                    'created': atoms[0],
                    'service': atoms[1],
                    'level': atoms[2],
                    'message': atoms[3]
                })
    except Exception as x:
        pass

    if reverse:
        errors.reverse()

    return errors
