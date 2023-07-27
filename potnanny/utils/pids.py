import os

PIDFILE = os.path.expanduser('~/.potnanny.pid')


def is_running(path=PIDFILE):
    """
    Check if an instance of the app is already running.
    args:
        - path to pidfile
    returns:
        - pid of running program, or 0 if not running.
    """

    if os.path.exists(path):
        st = os.stat(path)
        if st.st_size > 0:
            pid = pid_from_file(path)
            if check_pid(pid) is True:
                return pid
            else:
                os.unlink(path)
        else:
            os.unlink(path)

    return 0


def pid_from_file(path=PIDFILE):
    """
    Get pid number from named file
    args:
        - path to filename
    returns:
        - int (pid number)
    """

    with open(path, 'r') as fh:
        return int(fh.read())


def pid_to_file(pid, path=PIDFILE):
    """
    Write a pid to named file
    args:
        - pid number
        - path to filename
    """

    with open(path, 'w') as fh:
        fh.write(f"{pid}\n")


def check_pid(pid: int):
    """
    Check For the existence of a running unix pid
    args:
        - pid number
    returns:
        bool, running pid was found = True
    """

    try:
        os.kill(pid, 0)
    except OSError:
        return False

    return True
