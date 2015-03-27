import os
import stat
from tempfile import NamedTemporaryFile, TemporaryDirectory

from pytest import raises

from vimball import mkdir_p


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

