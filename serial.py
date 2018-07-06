#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import os
import sys
import subprocess as sp
import re
import configparser
import errno
import string

import string_helpers


EXTENSIONS = ["avi", "mkv", "mp4", "mpg"]
CONFIG_FILE = os.path.expanduser("~/.serial.py.conf")
player = "mpv"


class ConfigHelper():

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read(CONFIG_FILE)

    def get_episode_from_db(self, show_path):
        try:
            episode = self.config.getint('Main', show_path)
        except configparser.NoSectionError:
            episode = 0
        except configparser.NoOptionError:
            episode = 0
        return episode

    def save_episode_to_db(self, show_path, episode):
        try:
            self.config.add_section('Main')
        except configparser.DuplicateSectionError:
            pass
        self.config.set('Main', show_path, episode)
        with open(CONFIG_FILE, 'w') as config_file:
            self.config.write(config_file)

    def get_player(self):
        try:
            player = self.config.get('General', 'player')
        except configparser.NoSectionError:
            player = "mplayer"
        except configparser.KeyError:
            player = "mplayer"
        return player


class Serial():

    def __init__(self, action, episode=0):
        self.config = ConfigHelper()
        self.cwd = os.getcwd()
        self.files = [i for i in os.listdir(self.cwd)
                      if i.split('.')[-1].lower() in EXTENSIONS]
        self.files.sort()

        if episode == 0 and action == 'play':
            self.episode = self.config.get_episode_from_db(self.cwd)
            if (self.episode == 0):
                self.episode += 1
            self._s_play_episode(self.episode)
            self.config.save_episode_to_db(self.cwd, self.episode)
        elif action == 'play':
            self.episode = episode
            self._s_play_episode(self.episode)
        elif action == 'next':
            self.episode = self.config.get_episode_from_db(self.cwd) + 1
            self._s_play_episode(self.episode)
            self.config.save_episode_to_db(self.cwd, self.episode)
        elif action == 'set':
            self.episode = episode
            self._s_play_episode(self.episode)
            self.config.save_episode_to_db()

    def _s_play_episode(self, episode):
        """Plays the episode with given number"""
        path = self.generate_filename(episode)
        # запускаем плейер
        try:
            os.stat(path)
            s_play(path)
        except OSError:
            print("Episode {0} isn't here :(".format(episode))
            sys.exit(1)

    def generate_filename(self, episode):
        # constructing file name (including full path)
        try:
            self.constructor = Constructor(self.files, episode)
            path = os.path.join(self.cwd, self.constructor.construct(episode))
            self.create_subtitle_symlink(self.episode)
        except IndexError:
            path = ''
        return path

    def create_subfile_name(self, filename):
        return os.path.splitext(filename)[0] + ".ass"

    def create_subtitle_symlink(self, episode):
        self.constructor = Constructor(self.files, episode)
        filename = self.constructor.construct(episode)
        for roots, dirs, files in os.walk("."):
            subfile = os.path.normpath(self.create_subfile_name(
                os.path.join(roots, filename)))
            try:
                if (os.stat(os.path.join(os.getcwd(), subfile))):
                    os.symlink(subfile,
                               os.path.join(subfile.split(os.sep)[-1]))
                    break
            except OSError:
                pass


class Constructor():

    def __init__(self, files, episode=0):
        self.files = [i for i in files
                      if i.split('.')[-1].lower() in EXTENSIONS]
        self.episode = episode

    def construct(self, episode):
        self.episode = episode

        file_name = ""
        # 1st method
        try:
            file_name = self._construct_filename_dd_re()
        except IndexError:
            pass
        except TypeError:
            pass
        if file_name:
            return file_name

        # 2nd method
        file_name = self._construct_diff_with_re()
        if file_name in self.files:
            return file_name

    def _construct_filename_dd_re(self):
        re_comp = re.compile(r'0*' + str(self.episode) + r'.+')
        try:
            file_name = [re_comp.match(i) for i in self.files
                         if (re_comp.match(i) is not None)][0].group()
        except:
            file_name = None
        return file_name

    def _construct_diff_with_re(self, episode=0):
        # next line is for using in unit-test
        if (episode > 0):
            self.episode = episode

        basename = string_helpers.cmp_str(self.files[0],
                           self.files[-1])
        if (len(basename) == 0):
            basename = string_helpers.cmp_str(self.files[self.episode - 1],
                               self.files[self.episode])

        if (len(basename) == 0):
            basename = string_helpers.cmp_str(self.files[self.episode - 2],
                               self.files[self.episode - 1])

        regexp_string = '{0}{1}.*'.format(
            re.escape(basename.rstrip(string.digits)),
            str(self.episode).zfill(2)
        )
        regexp = re.compile(regexp_string)
        file_name = [f for f in self.files if regexp.match(f)][0]
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
            if re.match(regexp, i):
                return i

    def _find_diff(self, str1, str2):
        pos = 0
        length = 2
        if len(str1) != len(str2):
            print("These fucking filenames are uncomparable!")
            return (0, 0)
        for i in range(0, len(str1)):
            if str1[i] != str2[i]:
                if str1[i].isdigit:
                    if pos == 0:
                        pos = i - 1
                    elif inner:
                        length += 1
            else:
                continue
        return (pos, length)

    def _find_mask(self):
        files = self.files
        files.sort()

        diff = find_diff(files[0], files[1])
        (pos, length) = (diff[0], diff[1])
        return (pos, length)


def usage():
    print("Usage: serial.py [episode]\n" +
          "serial.py next - play next episode\n" +
          "serial.py set [episode] - set current episode to [episode]")
    sys.exit(1)


def s_play(path):
    """Run mplayer"""
    try:
        sp.call([player, path])
    except OSError as e:
        errstr = ""
        if e.errno == errno.ENOENT:
            errstr = "Error: {0} - {1}\nPlease, specify another video player".format(player, e.strerror)
        else:
            errstr = "error: " + e.strerror
        raise Exception(errstr)


def main():
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "h", ["help"])
    except:
        usage()

    configHelper = ConfigHelper()
    global player
    player = configHelper.get_player()

    if len(args) == 0:
        episode = 0
        action = 'play'
    elif len(args) == 1:
        if args[0].isdigit():
            action = 'play'
            episode = args[0]
        elif args[0] == 'play':
            action = 'play'
            episode = 0
        elif args[0] == 'next':
            episode = 0
            action = 'next'
        else:
            usage()
    elif len(args) == 2:
        if args[0] == 'set':
            episode = args[1]
            action = 'set'
        else:
            usage()
    else:
        print(len(args))
        print("error")
        return 1

    try:
        serial = Serial(action, int(episode))
    except Exception as e:
        print(e)
        return 1

if __name__ == "__main__":
    sys.exit(main())
