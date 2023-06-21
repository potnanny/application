import requests
import asyncio

def has_www(url='http://www.google.com'):
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


async def aio_has_www(url='http://www.google.com'):
    """
    Asyncio compatible way to check for internet connectivity
    args:
        - url (optional, defaults to google.com)
    returns:
        - bool
    """

    try:
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None,
            has_www, url)
        resp = await future
        return resp
    except:
        pass

    return False
