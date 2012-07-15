#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import unittest

from serial import find_diff, construct_diff_with_re, construct_filename_dd_re
from serial import Constructor


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
        self.assertIsNotNone(re.match(re_comp,
                                      "02. Тяжелое расставание.avi"))

    def test_construct_filename_dd_re(self):
        files = ["01. Первое знакомство.avi", "02. Тяжелое расставание.avi"]
        path = construct_filename_dd_re(1, files)
        self.assertEqual(path, "01. Первое знакомство.avi")
        path = construct_filename_dd_re(2, files)
        self.assertEqual(path, "02. Тяжелое расставание.avi")


class ConstructorTestCase(unittest.TestCase):

    files_diff_normal = ["[j22v] BLOOD-C - 01 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 02 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 03 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 04 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 05 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 06 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 07 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 08 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 09 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 10 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 11 (TBS 1280x720 x264).mp4",
                         "[j22v] BLOOD-C - 12 (TBS 1280x720 x264).mp4"
                         ]

    def test_constructor_diff_normal(self):
        constructor = Constructor(self.files_diff_normal)
        (pos, length) = constructor._find_diff(self.files_diff_normal[0],
                                               self.files_diff_normal[1])
        self.assertEqual(pos, 17)
        self.assertEqual(length, 2)

        self.assertEqual(constructor.construct(6),
                         self.files_diff_normal[5])

        files = ["Dantalian no Shoka - 01 (TX 1280x720 x264).mp4",
                 "Dantalian no Shoka - 02 (TX 1280x720 x264).mp4"]
        constructor = Constructor(files)
        self.assertEqual(constructor.construct(2),
                         files[1])

    def test_constructor_dd(self):
        files = ["01. Первое знакомство.avi", "02. Тяжелое расставание.avi"]
        constructor = Constructor(files)
        self.assertEqual(constructor.construct(1),
                         "01. Первое знакомство.avi")
        self.assertEqual(constructor.construct(2),
                         "02. Тяжелое расставание.avi")

    def test_find_diff_with_re(self):
        files = [
            "[Raws-4U] Amagami SS - 01 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 02 (TBS+BS-TBS 1280x720 H.264 AAC rev2).mp4",
            "[Raws-4U] Amagami SS - 03 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 04 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 05 (TBS 1280x720 H.264 AAC Chap rev2).mp4",
            "[Raws-4U] Amagami SS - 06 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 07 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 08 (TBS 1280x720 H.264 AAC Chap).mp4]"]
        self.assertEqual(
            construct_diff_with_re(2, files),
            files[1])
        self.assertEqual(
            construct_diff_with_re(4, self.files_diff_normal),
            self.files_diff_normal[3])

if __name__ == "__main__":
    unittest.main()
