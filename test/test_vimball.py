import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import mock

from mock import patch
from pytest import raises

from vimball import Vimball


def test_vimball():
    # nonexistent archive
    with raises(SystemExit):
        Vimball('nonexistent-archive.vba')

    # bad vimball archive
    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(b'bad archive')
        with raises(SystemExit):
            Vimball(tmpfile.name)

    with NamedTemporaryFile(mode='w+') as tmpfile:
        # use file basename when no extraction dir passed
        filename = os.path.basename(tmpfile.name)
        tmpfile.write('" Vimball Archiver')
        tmpfile.flush()
        v = Vimball(tmpfile.name)
        assert v.extractdir == filename

        # use custom dirname on name clash
        with TemporaryDirectory() as tmpdir:
            open(filename, 'w').close()
            with patch('vimball.tempfile.mkdtemp', return_value='vimball-randomfoo'):
                v = Vimball(tmpfile.name)
                assert v.extractdir == os.path.join('vimball-randomfoo', filename)

    # no files found in archive
    with NamedTemporaryFile(mode='w+') as tmpfile:
        filename = os.path.basename(tmpfile.name)
        tmpfile.write('" Vimball Archiver')
        tmpfile.flush()
        v = Vimball(tmpfile.name)
        assert list(v.files) == []
