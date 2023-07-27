import os
import unittest
from potnanny.utils import evaluate

class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_char_evals(self):
        assert evaluate("1 > 0") is True
        assert evaluate("0 < 1") is True
        assert evaluate("1 == 1") is True
        assert evaluate("1 >= 0") is True
        assert evaluate("0 <= 1") is True
        assert evaluate("0 != 1") is True
        assert evaluate("1 = 1") is True

    def test_str_evals(self):
        assert evaluate("1 gt 0") is True
        assert evaluate("0 lt 1") is True
        assert evaluate("1 eq 1") is True
        assert evaluate("1 ge 0") is True
        assert evaluate("0 le 1") is True
        assert evaluate("0 ne 1") is True


if __name__ == '__main__':
    unittest.main()
