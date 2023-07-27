import os
import unittest
import datetime
from potnanny.utils.pids import (pid_to_file, pid_from_file, check_pid, 
    is_running)


class TestPidFuncs(unittest.TestCase):
# ###############################################

    def test_running(self):
        path = '/tmp/test.pid'
        pid = os.getpid()
        pid_to_file(pid, path)
        assert is_running(path) == pid
        os.unlink(path)

    def test_pid_file(self):
        value = 9999
        path = '/tmp/test.pid'
        pid_to_file(value, path)

        assert os.path.exists(path)
        assert pid_from_file(path) == value

        os.unlink(path)

    def test_check_pid(self):
        pid = os.getpid()
        assert check_pid(pid) is True


if __name__ == '__main__':
    unittest.main()
