import os
import unittest
from potnanny.utils.numbers import is_number


class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_int(self):
        n = "13"
        assert is_number(n) == int

    def test_float(self):
        n = "13.0"
        assert is_number(n) == float

    def test_bogus(self):
        n = "bogus"
        assert is_number(n) == None


if __name__ == '__main__':
    unittest.main()
