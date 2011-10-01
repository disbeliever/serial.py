#!/usr/bin/python

import unittest

from serial import find_diff


class StringComparisonTestCase(unittest.TestCase):

    def testComp(self):
        series1 = "Dantalian no Shoka - 01 (TX 1280x720 x264).mp4)"
        series2 = "Dantalian no Shoka - 02 (TX 1280x720 x264).mp4)"
        (pos, length) = find_diff(series1, series2)
        self.assertEqual(pos, 21)
        self.assertEqual(length, 2)


if __name__ == "__main__":
    unittest.main()
