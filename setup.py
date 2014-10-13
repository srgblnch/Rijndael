#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: setup.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2014 (copyleft)
##
## This file is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This file is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this file.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import version
try:
    from Cython.Distutils import build_ext
    from setuptools import setup, Extension
    HAVE_CYTHON = True
except ImportError as e:
    HAVE_CYTHON = False
    warnings.warn(e.message)
    from distutils.core import setup, Extension
    from distutils.command import build_ext

GeneralizedRijndaelModule = Extension('GeneralizedRijndael',
                                      define_macros = [('MAJOR_VERSION',
                                                        '%d'%MAJOR_VERSION),
                                                       ('MINOR_VERSION',
                                                        '%d'%MINOR_VERSION),
                                                       ('BUILD_VERSION',
                                                        '%d'%BUILD_VERSION),
                                                       ('REVISION_VERSION',
                                                        '%d'%REVISION_VERSION)
                                                       ],
                                      sources = [
                                 'GeneralizedRijndael/GeneralizedRijndael.pyx',
                                                 ]
                                      )

configuration = {'name':'GeneralizedRijndael',
                 'version':'%d.%d.%d-%d'
                            %(MAJOR_VERSION,MINOR_VERSION,
                              BUILD_VERSION,REVISION_VERSION),
                 'license':'GPLv3+',
                 'description': "TODO: pending",
                 'long_description':'''TODO: Long description pending''',
                 'author':"Sergi Blanch-Torn\'e",
                 'author_email':"sblanch@alumnes.udl.cat",
                 'ext_modules': [GeneralizedRijndaelModule],
                 'cmdclass': {'build_ext': build_ext},
                 'classifiers':["Development Status :: 1 - Planning",
                                "Environment :: Console",
                                "Intended Audience :: Science/Research",
                                "License :: OSI Approved :: "\
                                     "GNU General Public License v3 or later "\
                                                                    "(GPLv3+)",
                                "Topic :: Security :: Cryptography"],
                 }

setup(**configuration)