import argparse
import bz2
import errno
from functools import partial
import gzip
import lzma
import os
import re
import sys
import tempfile

from vimball._version import __version__


def mkdir_p(path):
    """Create potentially nested directories as required.

    Does nothing if the path already exists and is a directory.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def is_vimball(fd):
    """Test for vimball archive format compliance.

    Simple check to see if the first line of the file starts with standard
    vimball archive header.
    """
    fd.seek(0)
    try:
        header = fd.readline()
    except UnicodeDecodeError:
        # binary files will raise exceptions when trying to decode raw bytes to
        # str objects in our readline() wrapper
        return False
    if re.match('^" Vimball Archiver', header) is not None:
        return True
    return False


def readline(fd):
    """Readline wrapper to force readline() to return str objects."""
    line = fd.__class__.readline(fd)
    if isinstance(line, bytes):
        line = line.decode()
    return line


class ArchiveError(Exception):
    """Catch-all archive error exception class."""
    pass


class Vimball:
    """Vimball archive format."""

    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise ArchiveError("vimball archive doesn't exist: {}".format(filepath))

        self.filepath = filepath
        _filebase, extension = os.path.splitext(filepath)
        if extension == ".gz":
            self.fd = gzip.open(filepath)
        elif extension == ".bz2":
            self.fd = bz2.BZ2File(filepath)
        elif extension == ".xz":
            self.fd = lzma.open(filepath)
        else:
            self.fd = open(filepath)

        # force readline() to always return str objects
        self.fd.readline = partial(readline, self.fd)

        if not is_vimball(self.fd):
            raise ArchiveError('Invalid vimball archive format')

    def __del__(self):
        try:
            self.fd.close()
        except AttributeError:
            return

    @property
    def files(self):
        """Yields archive file information."""
        # try new file header format first, then fallback on old
        for header in (r"(.*)\t\[\[\[1\n", r"^(\d+)\n$"):
            header = re.compile(header)
            filename = None
            self.fd.seek(0)
            line = self.fd.readline()
            while line:
                m = header.match(line)
                if m is not None:
                    filename = m.group(1)
                    try:
                        filelines = int(self.fd.readline().rstrip())
                    except ValueError:
                        raise ArchiveError('Invalid vimball archive format')
                    filestart = self.fd.tell()
                    yield (filename, filelines, filestart)
                line = self.fd.readline()
            if filename is not None:
                break

    def extract(self, extractdir=None, verbose=False):
        """Extract archive files to a directory."""
        if extractdir is None:
            filebase, extension = os.path.splitext(self.filepath)
            if extension in ('.gz', '.bz2', '.xz'):
                filebase, _extension = os.path.splitext(filebase)
            extractdir = os.path.basename(filebase)
            if os.path.exists(extractdir):
                tempdir = tempfile.mkdtemp(prefix='vimball-', dir=os.getcwd())
                extractdir = os.path.join(tempdir.split('/')[-1], extractdir)

        self.fd.seek(0)
        for filename, lines, offset in self.files:
            filepath = os.path.join(extractdir, filename)
            try:
                directory = os.path.dirname(filepath)
                mkdir_p(directory)
            except OSError as e:
                raise ArchiveError('Failed creating directory "{}": {}'.format(
                    directory, os.strerror(e.errno)))
            with open(filepath, 'w') as f:
                if verbose:
                    print(filepath)
                self.fd.seek(offset)
                for i in range(lines):
                    f.write(self.fd.readline())


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
        help='list files in a vimball archive')

    args = parser.parse_args()

    try:
        vimball = Vimball(args.archive[0])
        if args.extract:
            vimball.extract(args.extractdir, args.verbose)
        elif args.list:
            for filename, _lines, _offset in vimball.files:
                print(filename)
    except ArchiveError as e:
        raise SystemExit(e)
