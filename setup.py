#!/usr/bin/python

import os, sys, glob

name = 'biodas'
version = '0.1'

from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
    print("Cython not found")
else:
    use_cython = True

cmdclass = {}
ext_modules = []
print(use_cython)

metadata = {'name':name,
            'version': version,
            'cmdclass': cmdclass,
            'ext_modules': ext_modules,
            'description':'biodas',
            'author':'Jeffrey Hsu',
            'packages':['biodas'],
}


if __name__ == '__main__':
    dist = setup(**metadata)
