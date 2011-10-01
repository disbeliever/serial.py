#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import getopt
import os
import sys
import subprocess as sp
import re


extensions = ["avi", "mkv", "mp4", "mpg"]


def switch_bool(x):
    if x == False:
        res = True
    else:
        res = False
    return res


def usage():
    print "Usage: serial.py [series]"
    sys.exit(1)


def find_diff(str1, str2):
    pos = 0
    length = 2
    if len(str1) != len(str2):
        print "These fucking filenames are uncomparable!"
        return (0, 0)
    for i in xrange(0, len(str1)):
        if str1[i] != str2[i]:
            if str1[i].isdigit:
                if pos == 0:
                    pos = i - 1
                elif inner == True:
                    length += 1
        else:
            continue
    #print (pos, length)
    return (pos, length)


def find_mask(path):
    files = [i for i in os.listdir(path) if i.split('.')[-1] in extensions]
    files.sort()
    diff = find_diff(files[0], files[1])
    #print diff
    (pos, length) = (diff[0], diff[1])
    #print files[0][pos:pos + length]
    return (pos, length)

    #match_count = 0
    #for i in xrange(1, len(files)):
    #    match = re.search(r".*(0*{0}).*".format(i), files[i])
    #    if match:
    #        print "{0} {1} {2} {3}".format(i, match.group(0), match.group(1), match.pos)
    #        match_count += 1
    #print match_count


def is_first_run():
    # FIXME: how we do it?
    return False


def find_file(regexp):
    files = os.listdir(os.getcwd())
    for i in files:
        if re.match(regexp, i) and i.split('.')[-1] in extensions:
            return i


def parse_args():
    argc = sys.argc
    argv = sys.argv[1:]


def s_play(path, player="mplayer2"):
    """Запускает mplayer для проигрывания файла"""
    #sp.Popen([player, path])
    sp.call([player, path])


def s_play_series(series):
    # определяем имя файла для 1-й серии (это будет базовое имя файла)
    path = find_file(r'.*0*{0}.*'.format(1))
    # определяем позицию и длину подстроки, отвечающей за номер серии
    (pos, length) = find_mask(os.getcwd())
    # конструируем имя файла для нужной нам серии
    path = path[0:pos] + str(series).zfill(length) + path[pos + length:]
    # запускаем плейер
    try:
        os.stat(path)
        s_play(path)
    except OSError, e:
        #print "File not found: {0}".format(path)
        print "Series {0} isn't here :(".format(series)
        #return 1


def s_play_first():
    s_play_series(1)


def s_next():
    pass


def main():
    #actions = {
    #    "play": s_play,
    #    "next": s_next}

    #action = "play"

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "h", ["help"])
    except:
        usage()
    if len(args) == 1:
        series = args[0]
    else:
        series = 1

    if is_first_run():
        s_play_first()
    else:
        s_play_series(series)


if __name__ == "__main__":
    sys.exit(main())
