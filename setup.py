#!/usr/bin/env python
"""  Setup script. Used by easy_install and pip. """

import os
import sys
import re
import textwrap

from setuptools import setup, find_packages
from setuptools import Extension as Ext


"""Some functions for checking and showing errors and warnings."""


def _print_admonition(kind, head, body):
    tw = textwrap.TextWrapper(initial_indent='   ', subsequent_indent='   ')

    print(".. {0}:: {1}".format(kind.upper(), head))
    for line in tw.wrap(body):
        print(line)


def exit_with_error(head, body=''):
    _print_admonition('error', head, body)
    sys.exit(1)


def print_warning(head, body=''):
    _print_admonition('warning', head, body)


def check_import(pkgname, pkgver):
    """ Check for required Python packages. """
    try:
        mod = __import__(pkgname)
        if mod.__version__ < pkgver:
            raise ImportError
    except ImportError:
        exit_with_error(f"Can't find a local {pkgname} installation"
                        f" with version >= {pkgver}. "
                        f"Crossflow needs {pkgname} {pkgname} or greater"
                        " to compile and run! "
                        "Please see the ``README`` file.")

    print(f"* Found {pkgname} {mod.__version__} package installed.")
    globals()[pkgname] = mod


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


"""Discover the package version"""
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
VERSIONFILE = "crossflow/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError(f"Cannot find version string in {VERSIONFILE}.")


"""Check Python version"""
print("* Checking Python version...")
if sys.version_info[:2] < (3, 4):
    exit_with_error("You need Python 3.4+ to install crossflow!")
print("* Python version OK!")


"""Set up crossflow."""


class Extension(Ext, object):
    pass


setup_args = {
    'name':             "crossflow",
    'version':          verstr,
    'description':      "A Python workflows system",
    'long_description': read('README.md'),
    'author':           "Charlie Laughton",
    'author_email':     "charles.laughton@nottingham.ac.uk",
    'url':              "",
    'license':          "MIT license.",

    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

    'packages': find_packages(),

    'scripts': [
               ],

    'install_requires': [
                'dask',
                'distributed',
                'fsspec',
               ],

    'zip_safe': False,
}

setup(**setup_args)
