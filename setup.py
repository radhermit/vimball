#!/usr/bin/env python

from setuptools import setup


# workaround to get version without importing anything
with open('vimball/_version.py') as f:
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='vimball',
    version=__version__,
    description='a vimball extractor',
    long_description=readme,
    author='Tim Harder',
    author_email='radhermit@gmail.com',
    url='https://github.com/radhermit/vimball',
    license='MIT',
    packages=['vimball'],
    entry_points={'console_scripts': ['vimball = vimball:main']},
    platforms='Posix',
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
