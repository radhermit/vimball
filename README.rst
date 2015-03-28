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
