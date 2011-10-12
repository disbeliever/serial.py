#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import unittest

from serial import find_diff, construct_filename_dd_re


class MainTestCase(unittest.TestCase):

    def test_find_diff(self):
        series1 = "Dantalian no Shoka - 01 (TX 1280x720 x264).mp4)"
        series2 = "Dantalian no Shoka - 02 (TX 1280x720 x264).mp4)"
        (pos, length) = find_diff(series1, series2)
        self.assertEqual(pos, 21)
        self.assertEqual(length, 2)

    def test_dd_re(self):
        re_comp = r'0*' + str(1) + r'\D+'
        self.assertIsNotNone(re.match(re_comp, "01. Первое знакомство.avi"))
        self.assertIsNone(re.match(re_comp, "011. Первое знакомство.avi"))

        re_comp = r'0*' + str(2) + r'\D+'
        self.assertIsNotNone(re.match(re_comp, "02. Тяжелое расставание.avi"))

    def test_construct_filename_dd_re(self):
        files = ["01. Первое знакомство.avi", "02. Тяжелое расставание.avi"]
        path = construct_filename_dd_re(1, files)
        self.assertEqual(path, "01. Первое знакомство.avi")
        path = construct_filename_dd_re(2, files)
        self.assertEqual(path, "02. Тяжелое расставание.avi")

if __name__ == "__main__":
    unittest.main()
