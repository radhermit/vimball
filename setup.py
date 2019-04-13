#!/usr/bin/env python

import os
import re
import subprocess
import sys

from setuptools import setup, Command


class RunCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class PyTest(RunCommand):
    user_options = [('match=', 'k', 'Run only tests that match the provided expressions')]

    def initialize_options(self):
        self.match = None

    def run(self):
        cli_options = ['-k', self.match] if self.match else []
        os.environ['EPYTHON'] = 'python{}.{}'.format(sys.version_info.major, sys.version_info.minor)
        errno = subprocess.call(['py.test'] + cli_options)
        raise SystemExit(errno)


version = ''
with open('vimball/__init__.py', 'r', encoding='utf-8') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version')

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='vimball',
    version=version,
    description='a command-line vimball archive extractor',
    long_description=readme,
    author='Tim Harder',
    author_email='radhermit@gmail.com',
    url='https://github.com/radhermit/vimball',
    license='MIT',
    packages=['vimball'],
    entry_points={'console_scripts': ['vimball = vimball.cli:main']},
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    platforms='Posix',
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
)
