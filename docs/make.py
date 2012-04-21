#!/usr/bin/env python

"""
Python script for building documentation.

All dependencies for panGEO are required in order to build the documentation
due to the use of sphinx's autodoc extension which builds documentation from
doc strings.

Usage
-----
python make.py clean
python make.py html

Based on pandas make.py
"""

import glob
import os
import shutil
import sys

import sphinx

os.environ['PYTHONPATH'] = '..'

SPHINX_BUILD = 'sphinxbuild'

def clean():
    if os.path.exists('build'):
        shutil.rmtree('build')

def html():
    check_build()
    if os.system('sphinx-build -P -b html -d build/doctrees '
                 'source build/html'):
        raise SystemExit("Building HTML failed.")


def check_build():
    build_dirs = [
        'build', 'build/doctrees', 'build/html',
        ]
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass

def all():
    clean()
    print('Running all')
    pass

if __name__ == '__main__':
    funcd = {
        'html': html,
        'clean': clean,
        'all': all,
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            func = funcd.get(arg)
            if func is None:
                raise SystemExit('Unexpected command: %s; valid args are %s'%(
                    arg, funcd.keys()))
            func()
    else:
        all()
