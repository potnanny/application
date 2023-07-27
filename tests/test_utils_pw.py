import os
import unittest
import datetime
from potnanny.utils.pw import hash_password, verify_password

class TestPWHashUtils(unittest.TestCase):
# ###############################################

    def test_hashing(self):
        h1 = hash_password('foobar123')

        assert verify_password('foobar123', h1) is True
        assert verify_password('foobar123!', h1) is False

if __name__ == '__main__':
    unittest.main()
