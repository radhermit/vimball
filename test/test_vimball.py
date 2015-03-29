import os
import random
import stat
import string
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import mock

from mock import patch
from pytest import raises

from vimball import Vimball, mkdir_p, is_vimball, ArchiveError


class TemporaryVimPlugin(TemporaryDirectory):
    """Create and return a temporary vim plugin populated with random data."""

    def __init__(self, name):
        super(TemporaryVimPlugin, self).__init__(prefix=name)
        for i in range(self.dirs):
            dirpath = os.path.join(self.name, str(i))
            os.mkdir(dirpath)
            for j in range(random.randrange(5)):
                filepath = os.path.join(dirpath, str(j))
                with open(filepath, 'w+') as f:
                    for _ in range(random.randrange(100)):
                        line = ''.join(random.choice(
                            string.ascii_uppercase + string.digits) for _ in range(79))
                        f.write(line + '\n')


class TemporaryVimball(NamedTemporaryFile):
    """Create and return a temporary vimball archive."""

    def __init__(self, name):
        super(TemporaryVimball, self).__init__(prefix=name)
        with TemporaryVimPlugin(name) as plugin:
            Vimball(plugin).create(self.name)


def test_mkdir_p():
    # creating a simple dir and nested dir
    with TemporaryDirectory() as tmpdir:
        for path in ('new', 'new/path'):
            new_path = os.path.join(tmpdir, path)
            assert not os.path.exists(new_path)
            mkdir_p(new_path)
            assert os.path.isdir(new_path)

    # trying to create an existing dir shouldn't raise an OSError
    with TemporaryDirectory() as tmpdir:
        new_path = os.path.join(tmpdir, 'dir')
        os.mkdir(new_path)
        assert os.path.isdir(new_path)
        mkdir_p(new_path)
        assert os.path.isdir(new_path)

    # standard lack of permissions problem
    with TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'dir')
        os.mkdir(path)
        os.chmod(path, stat.S_IREAD)
        with raises(OSError):
            new_path = os.path.join(path, 'dir')
            mkdir_p(new_path)

    # creating a dir over an existing file isn't allowed
    with NamedTemporaryFile() as tmpfile:
        with raises(OSError):
            mkdir_p(tmpfile.name)


def is_vimball():
    # bad vimball archive
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(b'bad archive')
        tmpfile.flush()
        assert not is_vimball(tmpfile.name)

    # good vimball archive header
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write('" Vimball Archiver')
        tmpfile.flush()
        assert is_vimball(tmpfile.name)


def test_vimball():
    # nonexistent archive
    with raises(ArchiveError):
        Vimball('nonexistent-archive.vba')

    # bad vimball archive
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(b'bad archive')
        with raises(ArchiveError):
            Vimball(tmpfile.name)

    # no files found in archive
    with NamedTemporaryFile(mode='w+') as tmpfile:
        filename = os.path.basename(tmpfile.name)
        tmpfile.write('" Vimball Archiver')
        tmpfile.flush()
        v = Vimball(tmpfile.name)
        assert list(v.files) == []

    # with NamedTemporaryFile(mode='w+') as tmpfile:
    #     # use file basename when no extraction dir passed
    #     filename = os.path.basename(tmpfile.name)
    #     tmpfile.write('" Vimball Archiver')
    #     tmpfile.flush()
    #     v = Vimball(tmpfile.name)
    #     assert v.extractdir == filename
    #
    #     # use custom dirname on name clash
    #     with TemporaryDirectory() as tmpdir:
    #         open(filename, 'w').close()
    #         with patch('vimball.tempfile.mkdtemp', return_value='vimball-randomfoo'):
    #             v = Vimball(tmpfile.name)
    #             assert v.extractdir == os.path.join('vimball-randomfoo', filename)
