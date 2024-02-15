import os
import sys
import time
import logging
import asyncio
import signal
import argparse
from daemon import DaemonContext
from potnanny.utils.pids import PIDFILE, is_running, pid_to_file
from potnanny.utils import resolve_path
from potnanny.config import Config
from potnanny.app import run_app


args = None
logger = None


def main():
    parse_args()
    if args.action == 'start':
        start()
    elif args.action == 'stop':
        stop()
    elif args.action == 'status':
        status()
    elif args.action == 'restart':
        restart()
    else:
        sys.stderr.write(f"Unrecognized action '{args.action}'\n")
        sys.exit(1)


def start():
    print("Sevice starting")
    pid = is_running()
    if pid:
        sys.stderr.write(f"Service already running (pid {pid})\n")
        sys.exit(1)
    start_service()


def stop(die_absent=True):
    print("Service stopping")
    pid = is_running()
    if not pid:
        sys.stderr.write("Service not running\n")
        if die_absent:
            sys.exit(1)
    else:
        try:
            # pgid = os.getpgid(pid)
            # os.killpg(pgid, signal.SIGTERM)
            os.kill(pid, signal.SIGKILL)
        except Exception as x:
            print(x)
        finally:
            os.unlink(PIDFILE)
        print("Service stopped")


def status():
    print("Checking service")
    pid = is_running()
    if pid:
        print(f"Service running (pid {pid})")
        sys.exit(0)
    else:
        sys.stderr.write("Service not running\n")
        sys.exit(1)


def restart():
    stop(False)
    time.sleep(2)
    start()


def start_service():
    opts = {
        'stdout': None,
        'stderr': None
    }
    if args.debug:
        opts.update({
            'stdout': sys.stdout,
            'stderr': sys.stderr
        })

    with DaemonContext(**opts):
        config = Config()
        pid_to_file(os.getpid())
        init_logging(config.log_path)
        asyncio.run(run_app(config))


def init_logging(path=None):
    """
    Initialize logging to file, or stdout
    """

    global logger
    logger = logging.getLogger('potnanny')

    fmt = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'
    if path:
        path = resolve_path(path)

    if args.debug:
        level = logging.DEBUG
        logging.basicConfig(level=level, format=fmt)
        logging.getLogger('aiosqlite').setLevel(logging.INFO)
        logging.getLogger('bleak').setLevel(logging.INFO)
    else:
        level = logging.WARNING
        logging.basicConfig(filename=path, level=level, format=fmt)


def parse_args():
    global args
    parser = argparse.ArgumentParser(description='Potnanny worker and web service')
    parser.add_argument('action', choices=[
        'start', 'stop', 'restart', 'status'])
    parser.add_argument('-d','--debug', action='store_true',
        help='turn on debug messages')
    args = parser.parse_args()


if __name__ == '__main__':
    main()
