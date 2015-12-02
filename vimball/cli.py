import argparse
import sys

from vimball.base import Vimball, ArchiveError


argparser = argparse.ArgumentParser(description='vimball extractor', prog='vimball')

argparser.add_argument('archive', nargs=1)
argparser.add_argument('-v', '--verbose', action='store_true',
    help='show files names when extracting an archive')
argparser.add_argument('-C', '--directory', metavar='DIR', dest='extractdir',
    help='extract files to a specified directory')

actions = argparser.add_mutually_exclusive_group()
actions.add_argument('-x', '--extract', action='store_true',
    help='extract files from a vimball archive')
actions.add_argument('-l', '--list', action='store_true',
    help='list files in a vimball archive')


def parse_args(args):
    opts = argparser.parse_args(args)
    return opts


def main(args=None):
    args = args if args is not None else sys.argv[1:]
    opts = parse_args(args)

    try:
        vimball = Vimball(opts.archive[0])
        if opts.extract:
            vimball.extract(opts.extractdir, opts.verbose)
        elif opts.list:
            for filename, _lines, _offset in vimball.files:
                print(filename)
    except ArchiveError as e:
        raise SystemExit(e)
