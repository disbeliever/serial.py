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


class Serial():

    def __init__(self, action, episode=0):
        self.config = ConfigParser.RawConfigParser()
        self.cwd = os.getcwd()
        self.files = [i for i in os.listdir(self.cwd)
                      if i.split('.')[-1].lower() in extensions]
        self.files.sort()

        if episode == 0 and action == 'play':
            self.episode = self._get_episode_from_db()
            self._s_play_episode(self.episode)
            self._save_episode_to_db()
        elif action == 'play':
            self.episode = episode
            self._s_play_episode(self.episode)
        elif action == 'play' and episode == 0:
            self._get_episode_from_db()
            self._s_play_episode(self.episode)
        elif action == 'next':
            self.episode = self._get_episode_from_db() + 1
            self._s_play_episode(self.episode)
            self._save_episode_to_db()
        elif action == 'set':
            self.episode = episode
            self._s_play_episode(self.episode)
            self._save_episode_to_db()

    def action_play(self):
        pass

    def action_next(self):
        pass

    def _get_episode_from_db(self):
        self.config.read(CONFIG_FILE)

        try:
            episode = self.config.getint('Main', self.cwd)
        except ConfigParser.NoSectionError:
            episode = 1
        except ConfigParser.NoOptionError:
            episode = 1
        return episode

    def _save_episode_to_db(self):
        self.config.read(CONFIG_FILE)
        try:
            self.config.add_section('Main')
        except ConfigParser.DuplicateSectionError:
            pass
        self.config.set('Main', self.cwd, self.episode)
        with open(CONFIG_FILE, 'wb') as config_file:
            self.config.write(config_file)

    def _s_play(self, path, player="mplayer2"):
        """Запускает mplayer для проигрывания файла"""
        sp.call([player, path])

    def _s_play_episode(self, episode):
        # конструируем имя файла (включая полный путь)
        try:
            constructor = Constructor(self.files, episode)
            path = os.path.join(self.cwd, constructor.construct(episode))
            self.create_subtitle_symlink(self.episode)
        except IndexError:
            path = ''
        # запускаем плейер
        try:
            os.stat(path)
            s_play(path)
        except OSError, e:
            #print "File not found: {0}".format(path)
            print "Episode {0} isn't here :(".format(episode)
            sys.exit(1)

    def create_subtitle_symlink(self, episode):
        cons = Constructor(self.files, episode)
        filename = cons.construct(episode)
        p = os.getcwd()
        for roots, dirs, files in os.walk("."):
            try:
                subfile = (''.join(os.path.join(roots, filename).rsplit('.')[0:-1]) + \
                '.ass').replace('//', '/')[1:]
                print os.path.join(subfile)
                if (os.stat(os.path.join(os.getcwd(), subfile))):
                    os.symlink(subfile,
                    os.path.join(subfile.split(os.sep)[-1]))
                    #print "sub:", subfile
                    break
            except OSError:
                pass


class Constructor():

    def __init__(self, files, episode=0):
        self.files = files
        self.episode = episode

    def construct(self, episode):
        self.episode = episode
        # 1st method
        #file_name = self._construct_filename_find_diff()
        file_name = self._construct_diff_with_re()
        if file_name in self.files:
            return file_name
        # 2nd method
        try:
            file_name = self._construct_filename_dd_re()
        except IndexError:
            pass
        except TypeError:
            pass
        if file_name:
            return file_name

    def _construct_filename_dd_re(self):
        re_comp = re.compile(r'0*' + str(self.episode) + r'\D+')
        file_name = [re_comp.match(i) for i in self.files
                     if (re_comp.match(i) is not None
                         and i.split('.')[-1] in extensions)][0].group()
        return file_name

    def _construct_diff_with_re(self):
        try:
            basename = cmp_str(self.files[0],
                               self.files[1])
        except:
            basename = cmp_str(self.files[self.episode],
                               self.files[self.episode + 1])
        regexp_string = '{0}{1}.*'.format(re.escape(basename.rstrip('0')),
                                          str(self.episode).zfill(2))
        regexp = re.compile(regexp_string)
        file_name = filter(lambda x: regexp.match(x), self.files)[0]
        #except IndexError:
        #    return None
        #except TypeError:
        #    return None
        if file_name in self.files:
            return file_name
        else:
            return None

    def _construct_filename_find_diff(self):
        """
        Конструируем имя файла на основе поиска разницы.
        Работает для случаев вроде:
        Bla-bla - 01 tra-la-la.mkv
        Bla-bla - 02 tra-la-la.mkv
        """
        # определяем имя файла для 1-й серии (это будет базовое имя файла)
        path = self._find_file(r'.*0*{0}.*'.format(1))
        # определяем позицию и длину подстроки, отвечающей за номер серии
        (pos, length) = self._find_mask()
        if not path:
            return None
        # конструируем имя файла для нужной нам серии
        path = ''.join([path[0:pos],
                        str(self.episode).zfill(length),
                        path[pos + length:]])
        return path

    def _find_file(self, regexp):
        """Find file by given regexp"""
        for i in self.files:
            if re.match(regexp, i) and i.split('.')[-1] in extensions:
                return i

    def _find_diff(self, str1, str2):
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

    def _find_mask(self):
        files = [i for i in self.files if i.split('.')[-1] in extensions]
        files.sort()

        diff = find_diff(files[0], files[1])
        (pos, length) = (diff[0], diff[1])
        return (pos, length)


def cmp_str(str1, str2):
    """Находим общую часть в строках"""
    x = ''
    prev_match = True
    for i in xrange(0, len(str1)):
        if str1[i] == str2[i] and prev_match == True:
            x += str1[i]
        else:
            prev_match = False
    return x


def construct_diff_with_re(episode, files):
    basename = cmp_str(files[0], files[1])
    regexp = re.compile('{0}{1}.*'.format(re.escape(basename), episode))
    result = filter(lambda x: regexp.match(x), files)[0]
    return result


def switch_bool(x):
    if x == False:
        res = True
    else:
        res = False
    return res


def usage():
    print "Usage: serial.py [episode]"
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
    #try:
    diff = find_diff(files[0], files[1])
    #print diff
    (pos, length) = (diff[0], diff[1])
    #print files[0][pos:pos + length]
    return (pos, length)
    #except IndexError:
    #    print "[error]: Something wrong with indices in find_mask()"
    #    sys.exit(1)


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


def construct_filename_dd_re(episode, files):
    re_comp = re.compile(r'0*' + str(episode) + r'\D+')

    path = [re_comp.match(i) for i in files
            if (re_comp.match(i) is not None and
                i.split('.')[-1] in extensions)][0].group()
    return path


def construct_filename_find_diff(episode):
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
    path = path[0:pos] + str(episode).zfill(length) + path[pos + length:]
    return path


def construct_filename(episode):
    path = ""
    cwd = os.getcwd()
    # 1. First method
    try:
        path = os.path.join(cwd,
                            construct_filename_dd_re(int(episode),
                                                     os.listdir(cwd)))
    except IndexError:
        pass
    except TypeError:
        pass

    if path:
        print path
        return path
    else:
        # 2. Second method (difference-based)
        path = construct_filename_find_diff(episode)
        if path:
            return path


def s_play(path, player="mplayer2"):
    """Запускает mplayer для проигрывания файла"""
    sp.call([player, path])


def s_play_episode(episode):
    # конструируем имя файла (включая полный путь)
    path = construct_filename(episode)
    # запускаем плейер
    try:
        os.stat(path)
        s_play(path)
    except OSError, e:
        #print "File not found: {0}".format(path)
        print "Episode {0} isn't here :(".format(episode)
        #return 1


def s_play_first():
    s_play_episode(1)


def s_next():
    pass


def get_episode_from_db():
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)

    try:
        episode = config.getint('Main', os.getcwd())
    except ConfigParser.NoSectionError:
        episode = 1
    return episode


def save_episode_to_db(episode):
    import random
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_FILE)
    try:
        config.add_section('Main')
    except ConfigParser.DuplicateSectionError:
        pass
    config.set('Main', os.getcwd(), episode)
    with open(CONFIG_FILE, 'wb') as config_file:
        config.write(config_file)


def main():
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "h", ["help"])
    except:
        usage()

    if len(args) == 0:
        episode = 0
        action = 'play'
    elif len(args) == 1:
        if args[0].isdigit():
            action = 'play'
            episode = args[0]
        elif args[0] == 'play':
            action = 'play'
            episode = 1
        elif args[0] == 'next':
            episode = 0
            action = 'next'
    elif len(args) == 2:
        if args[0] == 'set':
            episode = args[1]
            action = 'set'
    else:
        print len(args)
        print "error"
        return 1

    serial = Serial(action, int(episode))

if __name__ == "__main__":
    sys.exit(main())
