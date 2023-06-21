import os
import unittest
import datetime
from potnanny.utils.temperature import convert_to_fahrenheit

class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_convert(self):
        assert convert_to_fahrenheit(0) == 32.0
        assert convert_to_fahrenheit(100) == 212.0

    def test_bogus(self):
        assert convert_to_fahrenheit("foo") == None


if __name__ == '__main__':
    unittest.main()
