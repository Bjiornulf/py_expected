import unittest
from py_expected import *


class TestExpected(unittest.TestCase):

    GOOD_VALUE = "good"
    ERROR = "bad"

    def test_value(self):
        good = Expected(self.GOOD_VALUE)
        self.assertTrue(isinstance(good.value(), type(self.GOOD_VALUE)))

    def test_error(self):
        bad = Expected.from_error(self.ERROR)
        self.assertTrue(isinstance(bad.error(), type(self.ERROR)))
        self.assertRaises(BadValueAccess, bad.value)


if __name__ == "__main__":
    unittest.main()
