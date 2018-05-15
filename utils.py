import argparse
from os.path import isdir, abspath
from os import makedirs as mkdir
from subprocess import run as bash

DEFAULT_DIR = abspath("dashes/")


def pip_install(package):
    package = package.split()[0].split(';')[0].split('&')[0].lower()
    print(bash(["pip", "install", package]))


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

