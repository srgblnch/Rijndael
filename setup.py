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


from setuptools import setup, find_packages
from GeneralizedRijndael import version


setup(name = 'GeneralizedRijndael',
      license = "GPLv3+",
      description = "Python prove of concept to generalize the rijndael's "\
                    "parameters.",
      version = version(),
      author = "Sergi Blanch-Torn\'e",
      author_email = "sblanch@cells.es",
      classifiers = ['Development Status :: 1 - Planning',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Information Technology',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: '\
                        'GNU General Public License v3 or later (GPLv3+)',
                     'Operating System :: POSIX',
                     #'Programming Language :: Cython',
                     'Programming Language :: Python',
                     'Topic :: Scientific/Engineering :: '\
                        'Interface Engine/Protocol Translator',
                     'Topic :: Software Development :: Embedded Systems',
                     'Topic :: Software Development :: Libraries :: '\
                        'Python Modules',
                     'Topic :: Scientific/Engineering :: Mathematics',
                     'Topic :: Security :: Cryptography',
                     ''],
      packages=find_packages(),
      url="https://github.com/srgblnch/Rijndael",
)

#for the classifiers review see:
#https://pypi.python.org/pypi?%3Aaction=list_classifiers
#
#Development Status :: 1 - Planning
#Development Status :: 2 - Pre-Alpha
#Development Status :: 3 - Alpha
#Development Status :: 4 - Beta
#Development Status :: 5 - Production/Stable

## TODO: cython
##############################################################################
# import sys
# import warnings
# from GeneralizedRijndael.version import *
# try:
#     from Cython.Distutils import build_ext
#     from setuptools import setup, Extension
#     from Cython.Build import cythonize
#     HAVE_CYTHON = True
# except ImportError as e:
#     HAVE_CYTHON = False
#     warnings.warn(e.message)
#     sys.exit(-1)
# 
# #FIXME: This shall produce only one .so with all the modules inside!
# #       But is generating one .so for each of the .py files
# extensions = [
# Extension('GeneralizedRijndael',
#           define_macros = [('MAJOR_VERSION',
#                             '%d'%MAJOR_VERSION),
#                            ('MINOR_VERSION',
#                             '%d'%MINOR_VERSION),
#                            ('BUILD_VERSION',
#                             '%d'%BUILD_VERSION),
#                            ('REVISION_VERSION',
#                             '%d'%REVISION_VERSION)
#                            ],
#           sources = [#'GeneralizedRijndael/*.py',
# #                    'GeneralizedRijndael/Logger.py',
# #                    'GeneralizedRijndael/ThirdLevel.py',
# #                    'GeneralizedRijndael/SBox.py',
# #                    'GeneralizedRijndael/RoundConstant.py',
# #                    'GeneralizedRijndael/KeyExpansion.py',
# #                    'GeneralizedRijndael/SubBytes.py',
# #                    'GeneralizedRijndael/ShiftRows.py',
# #                    'GeneralizedRijndael/MixColumns.py',
# #                    'GeneralizedRijndael/AddRoundKey.py',
#                     'GeneralizedRijndael/GeneralizedRijndael.py',
#                     ],
#           language = "c++"),
# Extension('Logger',['GeneralizedRijndael/Logger.py'],language='c++'),
# Extension('KeyExpansion',
#           ['GeneralizedRijndael/KeyExpansion.py'],language='c++'),
# Extension('SubBytes',['GeneralizedRijndael/SubBytes.py'],language='c++'),
# Extension('ShiftRows',['GeneralizedRijndael/ShiftRows.py'],language='c++'),
# Extension('MixColumns',['GeneralizedRijndael/MixColumns.py'],language='c++'),
# Extension('AddRoundKey',['GeneralizedRijndael/AddRoundKey.py'],language='c++'),
# Extension('SBox',['GeneralizedRijndael/SBox.py'],language='c++'),
# Extension('RoundConstant',['GeneralizedRijndael/RoundConstant.py'],
#           language='c++'),
# Extension('Polynomials',['GeneralizedRijndael/Polynomials.py'],language='c++'),
# Extension('ThirdLevel',['GeneralizedRijndael/ThirdLevel.py'],language='c++'),
# Extension('version',['GeneralizedRijndael/version.py'],language='c++'),
# ]
# 
# shortDescription = "Generalization of the rijndael for "\
#                    "academic cryptographic purposes"
# longDescription = \
# '''This is just a probe of concept. You MUST NOT use this code in production 
# projects.
# 
# The original schema of the Rijndael cryptosystem has one block size with 5 key 
# lenghts. During the AES contest process this was restricted to 3 known key 
# lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). 
# But the parameters flexibility of this schema allows even more posibilities.
# 
# The code has been made to academic cryptographic purposes and its 
# cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been 
# demonstrated its properties like the original Rijndael has. The side-channel 
# attacks neither wasn't studied yet, then they are not prevented in the current 
# code stage.
# '''
# 
# configuration = {'name':'GeneralizedRijndael',
#                  'version':'%d.%d.%d-%d'
#                             %(MAJOR_VERSION,MINOR_VERSION,
#                               BUILD_VERSION,REVISION_VERSION),
#                  'license':'GPLv3+',
#                  'description': shortDescription,
#                  'long_description':longDescription,
#                  'author':"Sergi Blanch-Torn\'e",
#                  'author_email':"sblanch@alumnes.udl.cat",
#                  #'ext_modules': extensions,
#                  'ext_modules':cythonize(extensions),
#                  'cmdclass': {'build_ext': build_ext},
#                  'classifiers':["Development Status :: 1 - Planning",
#                                 "Environment :: Console",
#                                 "Intended Audience :: Science/Research",
#                                 "License :: OSI Approved :: "\
#                                      "GNU General Public License v3 or later "\
#                                                                     "(GPLv3+)",
#                                 "Topic :: Security :: Cryptography"],
#                  }
# 
# setup(**configuration)
