import os
import unittest
from potnanny.utils.lists import flatten_list


class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_flatten(self):
        orig = ['foo', 'bar', ['baz', 'banana', ['apple']]]
        result = flatten_list(orig)
        assert len(result) == 5

if __name__ == '__main__':
    unittest.main()
