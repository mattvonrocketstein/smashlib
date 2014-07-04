#!/usr/bin/env python
""" setup.py for smash
"""

from setuptools import setup, find_packages

setup(
    name         = 'smash',
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    version      = '0.1',
    description  = 'SmaSh: a smart(er) shell',
    url          = 'http://github.com/mattvonrocketstein/smash',
    license      = 'MIT',
    keywords     = 'system shell',
    platforms    = 'any',
    zip_safe     = False,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    package_dir  = {'': 'lib'},
    packages     = find_packages('lib'),
    entry_points = \
    { 'console_scripts': \
      ['smash_shell = smashlib.bin.smash_shell:entry', ]
      }
    )
