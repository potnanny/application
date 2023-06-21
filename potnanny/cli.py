import os
import sys
import logging
import asyncio
import signal
import argparse
from daemon import DaemonContext
from potnanny.utils.pids import PIDFILE, is_running, pid_to_file
from potnanny.utils import resolve_path
from potnanny.config import Config
from potnanny.app import init_app


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
    print("Starting service")
    pid = is_running()
    if pid:
        sys.stderr.write("Service already running (pid {pid})\n")
        sys.exit(1)
    start_service()


def stop(die_absent=True):
    print("Stopping service")
    pid = is_running()
    if not pid:
        sys.stderr.write("Service not running\n")
        if die_absent:
            sys.exit(1)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass
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

        # quietly create the dirs
        # path = resolve_path(config.plugin_path)
        # os.makedirs(path, exist_ok=True)

        pid_to_file(os.getpid())
        init_logging(config.log_path)
        asyncio.run(init_app(config))


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
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
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
