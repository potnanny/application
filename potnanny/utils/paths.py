import os

def resolve_path(path:str) -> str:
    """
    expand path to fully qualified, absolute path name
    """

    return os.path.abspath(os.path.expanduser(path))
