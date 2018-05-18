import argparse
from os.path import isdir, abspath, isfile
from os import makedirs as mkdir
import os
from subprocess import run as bash
from os import listdir as ls

DEFAULT_DIR = abspath("dashes/")


def generate_tab_list():
    tab_list = []
    for filename in sorted([f for f in ls(get_directory()) if isdir(os.path.join(get_directory(), f)) and isfile(os.path.join(get_directory(), f, f + ".py"))]):
        tab_list.append({'label': filename, 'value': filename})
    return tab_list


def write_file(name, contents, override=False):
    if override == True or name[:-3] not in ls(get_directory()):
        if not isdir(os.path.join(get_directory(), name[:-3])):
            mkdir(os.path.join(get_directory(), name[:-3]))
        with open(os.path.join(get_directory(), name[:-3], name), 'wb') as f:
            f.write(contents)
            return True
    return False


def pip_install(package):
    package = package.split()[0].split(';')[0].split('&')[0].lower()
    return bash(["pip", "install", package]).returncode


def get_directory():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="sets directory for storing files", default=DEFAULT_DIR)
    args = parser.parse_args()
    if not isdir(args.directory):
        if args.directory == DEFAULT_DIR:
            mkdir(args.directory)
        else:
            print("No such directory: %s" % args.directory)
            exit(0)
    return args.directory

