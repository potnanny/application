import requests
import asyncio
import aiohttp

def has_www(url='http://www.example.com'):
    """
    Check for internet connectivity
    args:
        - url (optional, defaults to google.com)
    returns:
        - bool
    """

    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return True
    except:
        pass

    return False


async def aio_has_www(url='http://www.example.com'):
    """
    Asyncio compatible way to check for internet connectivity
    args:
        - url (optional, defaults to google.com)
    returns:
        - bool
    """

    success = False
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                success = True

    return success
