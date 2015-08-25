import bz2
import errno
import gzip
import lzma
import os
import re
import tempfile


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

        if not is_vimball(self.fd):
            raise ArchiveError('Invalid vimball archive format')

    def __del__(self):
        try:
            self.fd.close()
        except AttributeError:
            return

    def readline(self):
        """Readline wrapper to force readline() to return str objects."""
        line = self.fd.__class__.readline(self.fd)
        if isinstance(line, bytes):
            line = line.decode()
        return line

    @property
    def files(self):
        """Yields archive file information."""
        # try new file header format first, then fallback on old
        for header in (r"(.*)\t\[\[\[1\n", r"^(\d+)\n$"):
            header = re.compile(header)
            filename = None
            self.fd.seek(0)
            line = self.readline()
            while line:
                m = header.match(line)
                if m is not None:
                    filename = m.group(1)
                    try:
                        filelines = int(self.readline().rstrip())
                    except ValueError:
                        raise ArchiveError('Invalid vimball archive format')
                    filestart = self.fd.tell()
                    yield (filename, filelines, filestart)
                line = self.readline()
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
                    f.write(self.readline())
