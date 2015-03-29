|pypi| |test| |coverage|

=======
vimball
=======

vimball is a simple command-line tool for extracting vimball archives.

For extracting vimball archives use the following command::

    vimball -x <vimball archive>

By default, vimball will try to choose a directory that is named similar to the
vimball archive to extract the archive's files into. A specific directory name
or path may also be selected using the following::

    vimball -x <vimball archive> -C <extraction dir>

Listing the files contained inside the vimball archive is also supported using::

    vimball -l <vimball archive>


.. |pypi| image:: https://img.shields.io/pypi/v/vimball.svg
    :target: https://pypi.python.org/pypi/vimball
.. |test| image:: https://travis-ci.org/radhermit/vimball.svg?branch=master
    :target: https://travis-ci.org/radhermit/vimball
.. |coverage| image:: https://coveralls.io/repos/radhermit/vimball/badge.png?branch=master
    :target: https://coveralls.io/r/radhermit/vimball?branch=master
