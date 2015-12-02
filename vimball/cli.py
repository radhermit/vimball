import argparse
import sys

from vimball.base import Vimball, ArchiveError


argparser = argparse.ArgumentParser(description='vimball extractor', prog='vimball')

argparser.add_argument('path', nargs='+')
argparser.add_argument('-v', '--verbose', action='store_true',
    help='show files names when extracting an archive')
argparser.add_argument('-C', '--directory', metavar='DIR', dest='extractdir',
    help='extract files to a specified directory')

actions = argparser.add_mutually_exclusive_group()
actions.add_argument('-c', '--create', action='store_true',
    help='create a vimball archive')
actions.add_argument('-x', '--extract', action='store_true',
    help='extract files from a vimball archive')
actions.add_argument('-l', '--list', action='store_true',
    help='list files in a vimball archive')


def parse_args(args):
    for idx, arg in enumerate(args):
        if arg == '-c':
            if len(args) >= i+1 and args[i+1]:
                pass

    opts = argparser.parse_args(args)
    if opts.create is None and opts.path is None:
        argparser.error('missing required path argument')
    print(opts)
    opts.path = opts.path[0]
    return opts


def main(args=None):
    args = args if args is not None else sys.argv[1:]
    opts = parse_args(args)

    try:
        vimball = Vimball(opts.path, create=(opts.create is not None))
        if opts.extract:
            vimball.extract(opts.extractdir, opts.verbose)
        elif opts.create is not None:
            vimball.create(opts.create, opts.verbose)
        elif opts.list:
            for filename, _lines, _offset in vimball.files:
                print(filename)
    except ArchiveError as e:
        raise SystemExit('vimball: error: {}'.format(e))
