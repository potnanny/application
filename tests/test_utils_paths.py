import os
import unittest
from potnanny.utils.paths import resolve_path

class TestUtilFuncs(unittest.TestCase):
# ###############################################

    def test_path(self):
        result = resolve_path('~')
        assert result == os.path.abspath(os.getenv('HOME'))


if __name__ == '__main__':
    unittest.main()
