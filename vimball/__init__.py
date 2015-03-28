import argparse
import bz2
import gzip
import lzma
import os
import re
import sys
import tempfile

from vimball._version import __version__
from vimball.utils import mkdir_p


def is_vimball(fd):
    fd.seek(0)
    if re.match('^" Vimball Archiver', fd.readline()) is not None:
        return True
    return False


class Vimball:
    def __init__(self, filepath, extractdir=None, verbose=False):
        if not os.path.exists(filepath):
            raise SystemExit("vimball archive doesn't exist: {}".format(filepath))

        self.filepath = filepath
        self.verbose = verbose

        filebase, extension = os.path.splitext(filepath)
        if extension == ".gz":
            self._file = gzip.open(filepath)
        elif extension == ".bz2":
            self._file = bz2.BZ2File(filepath)
        elif extension == ".xz":
            self._file = lzma.open(filepath)
        else:
            self._file = open(filepath)

        if not is_vimball(self._file):
            raise SystemExit('Invalid vimball archive format')

        if extractdir is None:
            extractdir = os.path.basename(filebase)
            if os.path.exists(extractdir):
                tempdir = tempfile.mkdtemp(prefix='vimball-', dir=os.getcwd())
                extractdir = os.path.join(tempdir.split('/')[-1], extractdir)
        self.extractdir = extractdir

    def __del__(self):
        try:
            self._file.close()
        except AttributeError:
            return

    @property
    def files(self):
        # try new file header format first, then fallback on old
        for header in (r"(.*)\t\[\[\[1\n", r"^(\d+)\n$"):
            header = re.compile(header)
            filename = None
            self._file.seek(0)
            line = self._file.readline()
            while line:
                m = header.match(line)
                if m is not None:
                    filename = m.group(1)
                    try:
                        filelines = int(self._file.readline().rstrip())
                    except ValueError:
                        raise SystemExit('Invalid vimball archive format')
                    filestart = self._file.tell()
                    yield (filename, filelines, filestart)
                line = self._file.readline()
            if filename is not None:
                break

    def list(self):
        for filename, _lines, _offset in self.files:
            print(filename)

    def extract(self):
        self._file.seek(0)
        for filename, lines, offset in self.files:
            filepath = os.path.join(self.extractdir, filename)
            try:
                directory = os.path.dirname(filepath)
                mkdir_p(directory)
            except OSError:
                raise SystemExit('Failed creating directory: {}'.format(directory))
            with open(filepath, 'w') as f:
                if self.verbose:
                    print(filepath)
                self._file.seek(offset)
                for i in range(lines):
                    f.write(self._file.readline())


def main():
    parser = argparse.ArgumentParser(description='vimball extractor', prog='vimball')

    parser.add_argument('archive', nargs=1)
    parser.add_argument('-v', '--verbose', action='store_true',
        help='show files names when extracting an archive')
    parser.add_argument('-C', '--directory', metavar='DIR', dest='extractdir',
        help='extract files to a specified directory')

    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('-x', '--extract', action='store_true',
        help='extract files from a vimball archive')
    actions.add_argument('-l', '--list', action='store_true',
        help='list files a vimball archive')

    args = parser.parse_args()
    vimball = Vimball(args.archive[0], args.extractdir, args.verbose)

    if args.extract:
       vimball.extract()
    elif args.list:
       vimball.list()
