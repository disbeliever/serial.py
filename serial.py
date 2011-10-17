#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import getopt
import os
import sys
import subprocess as sp
import re
import ConfigParser


extensions = ["avi", "mkv", "mp4", "mpg"]
CONFIG_FILE = os.path.expanduser("~/.serial.py.conf")


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
    try:
        diff = find_diff(files[0], files[1])
        #print diff
        (pos, length) = (diff[0], diff[1])
        #print files[0][pos:pos + length]
        return (pos, length)
    except IndexError:
        print "[error]: Something wrong with indices in find_mask()"
        sys.exit(1)


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


def construct_filename_dd_re(series, files):
    re_comp = re.compile(r'0*' + str(series) + r'\D+')

    path = [re_comp.match(i) for i in files if (re_comp.match(i) is not None and i.split('.')[-1] in extensions)][0].group()
    return path


def construct_filename_find_diff(series):
    """
    Конструируем имя файла на основе поиска разницы.
    Работает для случаев вроде:
    Bla-bla - 01 tra-la-la.mkv
    Bla-bla - 02 tra-la-la.mkv
    """
    # определяем имя файла для 1-й серии (это будет базовое имя файла)
    path = find_file(r'.*0*{0}.*'.format(1))
    # определяем позицию и длину подстроки, отвечающей за номер серии
    (pos, length) = find_mask(os.getcwd())
    # конструируем имя файла для нужной нам серии
    path = path[0:pos] + str(series).zfill(length) + path[pos + length:]
    return path


# def construct_filename(series):
#     ls = os.listdir(os.getcwd())
#     num_re = re.compile(r'.*0*?' + series + '.*')
#     print ls[0]
#     print [i for i in ls if num_re.match(i)]
#     return path


def construct_filename(series):
    path = ""
    cwd = os.getcwd()
    # 1. First method
    try:
        path = os.path.join(cwd, construct_filename_dd_re(int(series), os.listdir(cwd)))
    except IndexError:
        pass
    except TypeError:
        pass

    if path:
        print path
        return path
    else:
        # 2. Second method (difference-based)
        path = construct_filename_find_diff(series)
        if path:
            return path


def s_play(path, player="mplayer2"):
    """Запускает mplayer для проигрывания файла"""
    sp.call([player, path])


def s_play_series(series):
    # конструируем имя файла (включая полный путь)
    path = construct_filename(series)
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


def get_series_from_db():
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)

    try:
        series = config.getint('Main', os.getcwd())
    except ConfigParser.NoSectionError:
        series = 1 
    return series


def save_series_to_db(series):
    import random
    config = ConfigParser.RawConfigParser()
    config.add_section('Main')
    config.set('Main', os.getcwd(), series)
    with open(CONFIG_FILE, 'wb') as config_file:
        config.write(config_file)


def main():
    #actions = {
    #    "play": s_play,
    #    "next": s_next }

    #action = "play"

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "h", ["help"])
    except:
        usage()
    if len(args) == 0:
        series = get_series_from_db()
    elif len(args) == 1:
        if args[0].isdigit():
            series = args[0]
        elif args[0] == 'play':
            series = get_series_from_db()
            save_series_to_db(series)
        elif args[0] == 'next':
            series = get_series_from_db() + 1
            save_series_to_db(series)
    elif len(args) == 2:
        if args[0] == 'set':
            series = args[1]
            save_series_to_db(series)
    else:
        print len(args)
        print "error"
        return 1

    # if is_first_run():
    #     s_play_first()
    # else:
    s_play_series(series)


if __name__ == "__main__":
    sys.exit(main())
