#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import unittest

from serial import Constructor, Serial
import string_helpers


class StringHelperTestCase(unittest.TestCase):

    def test_get_shared_part(self):
        str1 = "abc123"
        str2 = "abc456"
        self.assertEqual(string_helpers.get_shared_part(str1, str2), "abc")


class MainTestCase(unittest.TestCase):

    def runTest(self):
        self.test_trim_down()

    def test_find_diff(self):
        constructor = Constructor([])
        series1 = "Dantalian no Shoka - 01 (TX 1280x720 x264).mp4)"
        series2 = "Dantalian no Shoka - 02 (TX 1280x720 x264).mp4)"
        (pos, length) = constructor._find_diff(series1, series2)
        self.assertEqual(pos, 21)
        self.assertEqual(length, 2)

    def test_construct_filename_dd_re(self):
        files = ["01. Первое знакомство.avi", "02. Тяжелое расставание.avi"]
        constructor = Constructor(files)

        path = constructor._construct_filename_dd_re()
        self.assertEqual(path, "01. Первое знакомство.avi")

        constructor.episode = 2
        path = constructor._construct_filename_dd_re()
        self.assertEqual(path, "02. Тяжелое расставание.avi")

    def test_trim_down(self):
        files = ["[Commie] Haikyuu!! - 08 [13E5217D].mkv",
                 "[mohbaboo-subs] Haikyuu!! - 09 [1B080828].mkv"]
        self.assertEqual(
            string_helpers.trim_down(files[0], files[1]),
            ("[Commie] Haikyuu!! - 08 [13E5217D].mkv",
             "oo-subs] Haikyuu!! - 09 [1B080828].mkv"))


class SymlinkCreatorTestCase(unittest.TestCase):

    def test_base(self):
        serial = Serial("none")
        self.assertEqual(serial.create_subfile_name("/home/test/video.mkv"),
                         "/home/test/video.ass")


class ConstructorTestCase(unittest.TestCase):

    def runTest(self):
        self.test_different_raws()

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

        files = ["01. Бюро общественной безопасности, 9-й отдел.mkv",
                 "02. Испытание.mkv",
                 "03. Андроид и я.mkv",
                 "04. Перехватчик.mkv",
                 "05. Приманка.mkv",
                 "06. Подражатели.mkv",
                 "07. Идолопоклонничество.mkv",
                 "08. Пропавшие сердца.mkv",
                 "09. Чат! Чат! Чат!.mkv",
                 "10. Война в джунглях.mkv",
                 "11. Портреты.mkv",
                 "12. Побег.mkv",
                 "13. Неравенство.mkv"]
        constructor = Constructor(files)
        self.assertEqual(constructor.construct(5),
                         files[4])
        self.assertEqual(constructor.construct(6),
                         files[5])
        self.assertEqual(constructor.construct(7),
                         files[6])

    def test_find_diff_with_re(self):
        files = [
            "[Raws-4U] Amagami SS - 01 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 02 (TBS+BS-TBS 1280x720 H.264 AAC rev2).mp4",
            "[Raws-4U] Amagami SS - 03 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 04 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 05 (TBS 1280x720 H.264 AAC Chap rev2).mp4",
            "[Raws-4U] Amagami SS - 06 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 07 (TBS 1280x720 H.264 AAC Chap).mp4",
            "[Raws-4U] Amagami SS - 08 (TBS 1280x720 H.264 AAC Chap).mp4"]
        constructor = Constructor(files)
        self.assertEqual(
            constructor._construct_diff_with_re_backward(2),
            files[1])
        self.assertEqual(
            constructor._construct_diff_with_re_backward(4),
            files[3])

    def test_find_diff_with_re_2(self):
        files = [
            "[UTW]_Fate_Zero_-_14_[h264-720p][4D1CAEDB].mkv",
            "[UTW]_Fate_Zero_-_15_[h264-720p][422C8FDD].mkv",
            "[UTW]_Fate_Zero_-_16_[h264-720p][02A33212].mkv",
            "[UTW]_Fate_Zero_-_17_[h264-720p][F058E092].mkv",
            "[UTW]_Fate_Zero_-_18_[h264-720p][CFAB3675].mkv",
            "[UTW]_Fate_Zero_-_19_[h264-720p][EE7D8586].mkv",
            "[UTW]_Fate_Zero_-_20_[h264-720p][AF35659F].mkv",
            "[UTW]_Fate_Zero_-_21_[h264-720p][BCB5C808].mkv",
            "[UTW]_Fate_Zero_-_22_[h264-720p][6F59864F].mkv",
            "[UTW]_Fate_Zero_-_23_[h264-720p][9AD1A48A].mkv",
            "[UTW]_Fate_Zero_-_24_[h264-720p][583D3DBB].mkv",
            "[UTW]_Fate_Zero_-_25_[h264-720p][DEBA6F45].mkv"
            ]
        constructor = Constructor(files, 15)
        self.assertEqual(
            constructor._construct_diff_with_re_forward(),
            files[1])

        constructor = Constructor(files, 25)
        self.assertEqual(
            constructor._construct_diff_with_re_forward(),
            files[-1])

    def test_different_raws(self):
        files = ["[Commie] Haikyuu!! - 01 [5CB6E137].mkv",
                 "[Commie] Haikyuu!! - 02 [87E40A94].mkv",
                 "[Commie] Haikyuu!! - 03 [80B4441C].mkv",
                 "[Commie] Haikyuu!! - 04 [9E537287].mkv",
                 "[Commie] Haikyuu!! - 05 [009570F4].mkv",
                 "[Commie] Haikyuu!! - 06 [AAE4F869].mkv",
                 "[Commie] Haikyuu!! - 07 [572852D7].mkv",
                 "[Commie] Haikyuu!! - 08 [13E5217D].mkv",
                 "[mohbaboo-subs] Haikyuu!! - 09 [1B080828].mkv",
                 "[mohbaboo-subs] Haikyuu!! - 10 [7FF0CBA2].mkv"]
        constructor = Constructor(files)
        self.assertEqual(
            constructor.construct(1),
            files[0])

        self.assertEqual(
            constructor.construct(8),
            files[7])

    def test_sNeNN(self):
        files = [
            "s5e01_The Wedding.mkv",
            "s5e02_Six Forgotten Warriors.mkv",
            "s5e03_Unclaimed Legacy.mkv"]
        constructor = Constructor(files)
        self.assertEqual(
            constructor.construct(1),
            files[0])
        self.assertEqual(
            constructor.construct(3),
            files[2])

if __name__ == "__main__":
    unittest.main()
