import argparse
from os.path import isdir, abspath
from os import makedirs as mkdir
import os
from subprocess import run as bash
from os import listdir as ls

DEFAULT_DIR = abspath("dashes/")


def write_file(name, contents, override=False):
    if override == True or name not in ls(get_directory()):
        with open(os.path.join(get_directory(), name), 'wb') as f:
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

