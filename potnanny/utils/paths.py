import os

def resolve_path(path):
    """
    expand path to fully qualified, absolute path name
    args:
        - str (pathname)
    returns:
        str (path)
    """

    return os.path.abspath(os.path.expanduser(path))
