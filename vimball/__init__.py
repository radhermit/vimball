import argparse
import bz2
import errno
import gzip
import os
import re
import sys
import tempfile

from vimball._version import __version__
from vimball.exceptions import NoFilesFound
from vimball.utils import mkdir_p


class Vimball:
    def __init__(self, filepath, extractdir=None, verbose=False):
        self.filepath = filepath
        self.verbose = verbose

        filebase, extension = os.path.splitext(filepath)
        try:
            if extension == ".gz":
                self._file = gzip.open(filepath)
            elif extension == ".bz2":
                self._file = bz2.BZ2File(filepath)
            else:
                self._file = open(filepath)
        except IOError:
            print("That file doesn't exist!")
            sys.exit(errno.ENOENT)

        if not self._is_vimball():
            raise TypeError

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

    def _is_vimball(self):
        self._file.seek(0)
        header = self._file.readline()
        m = re.match('^" Vimball Archiver', header)

        if m is not None:
            return True
        else:
            return False

    def _find_files(self, header):
        filename = None
        self._file.seek(0)
        line = self._file.readline()
        while line:
            m = header.match(line)
            if m is not None:
                filename = m.group(1)
                filelines = int(self._file.readline().rstrip())
                filestart = self._file.tell()
                yield (filename, filelines, filestart)
            line = self._file.readline()

        if filename is None:
            raise NoFilesFound

    @property
    def files(self):
        header = re.compile(r"(.*)\t\[\[\[1\n")
        try:
            return self._find_files(header)
        except NoFilesFound:
            header = re.compile(r"^(\d+)\n$")
            try:
                return self._find_files(header)
            except NoFilesFound:
                raise SystemExit('No files were found in archive: {}'.format(self.filepath))

    def list(self):
        for (filename, lines, offset) in self.files:
            print(filename)

    def extract(self):
        self._file.seek(0)
        for (filename, lines, offset) in self.files:
            filepath = os.path.join(self.extractdir, filename)
            mkdir_p(os.path.dirname(filepath))
            with open(filepath, 'w') as f:
                if self.verbose:
                    print(filepath)
                self._file.seek(offset)
                for i in xrange(lines):
                    f.write(self._file.readline())


def main():
    parser = argparse.ArgumentParser(description='vimball extractor', prog='vimball')

    parser.add_argument('archive', nargs=1)
    parser.add_argument('-x', '--extract', action='store_true',
        help='extract files from a vimball archive')
    parser.add_argument('-l', '--list', action='store_true',
        help='list files a vimball archive')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='show files names when extracting an archive')
    parser.add_argument('-C', '--directory', metavar='DIR', dest='extractdir',
        help='extract files to a specified directory')

    args = parser.parse_args()
    vimball = Vimball(args.archive[0], args.extractdir, args.verbose)

    if args.extract:
       vimball.extract()
    elif args.list:
       vimball.list()
