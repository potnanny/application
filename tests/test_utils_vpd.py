import os
import unittest
import datetime
from potnanny.utils.vpd import calculate_vpd

class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_calc(self):
        result = calculate_vpd(24.0, 55.0)
        assert result == 1.34


if __name__ == '__main__':
    unittest.main()
