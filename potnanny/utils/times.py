import datetime


def utcnow(dt=None):
    """
    Get a UTC datetime obj, but with second and microsecond field set to zero.
    This should be used for all measurement datetime objects in potnanny.

    args:
        datetime obj (optional)
    returns:
        utc datetime obj
    """

    if dt is None:
        dt = datetime.datetime.utcnow()

    return dt.replace(second=0, microsecond=0)


def datetime_from_iso(iso):
    """
    Get datetime object from a javascript ISO Date string
    args:
        - str, like '2021-03-14T00:24:41.123Z'
    returns:
        datetime obj
    """

    try:
        # try utc tz conversion first
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%f%z")
    except:
        pass

    try:
        # try utc tz conversion first
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        pass

    try:
        # try timestamp without tz
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        pass

    try:
        # try timestamp without tz
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S")
    except:
        pass

    return None


def datetime_from_sqlite(txt):
    """
    Get datetime object from a sqlite formatted datetime str
    args:
        - str, like '2021-03-14 00:24:41.123'
    returns:
        datetime obj
    """

    try:
        return datetime.datetime.strptime(txt, "%Y-%m-%d %H:%M:%S.%f")
    except:
        pass

    try:
        return datetime.datetime.strptime(txt, "%Y-%m-%d %H:%M:%S")
    except:
        pass

    return None


def iso_from_sqlite(txt, utc=True):
    """
    Get iso repr of datetime object from a sqlite formatted datetime str
    args:
        - str, like '2021-03-14 00:24:41.123'
        - utc (is the sqlite datetime string in UTC)
    returns:
        iso datetime str, like '2021-03-28T00:24:41.123Z'
    """

    dt = datetime_from_sqlite(txt)
    if dt:
        if utc:
            return dt.isoformat() + "Z"
        else:
            return dt.isoformat()
    else:
        return None

