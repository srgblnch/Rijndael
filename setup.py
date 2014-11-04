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

import sys
import warnings
from version import *
try:
    from Cython.Distutils import build_ext
    from setuptools import setup, Extension
    HAVE_CYTHON = True
except ImportError as e:
    HAVE_CYTHON = False
    warnings.warn(e.message)
    sys.exit(-1)

extensions = [
Extension('GeneralizedRijndael',
          define_macros = [('MAJOR_VERSION',
                            '%d'%MAJOR_VERSION),
                           ('MINOR_VERSION',
                            '%d'%MINOR_VERSION),
                           ('BUILD_VERSION',
                            '%d'%BUILD_VERSION),
                           ('REVISION_VERSION',
                            '%d'%REVISION_VERSION)
                           ],
          sources = ['GeneralizedRijndael/GeneralizedRijndael.py'],
          language = "c++"),
Extension('Logger',['GeneralizedRijndael/Logger.py'],language='c++'),
Extension('KeyExpansion',
          ['GeneralizedRijndael/KeyExpansion.py'],language='c++'),
Extension('SubBytes',['GeneralizedRijndael/SubBytes.py'],language='c++'),
Extension('ShiftRows',['GeneralizedRijndael/ShiftRows.py'],language='c++'),
Extension('MixColumns',['GeneralizedRijndael/MixColumns.py'],language='c++'),
Extension('AddRoundKey',['GeneralizedRijndael/AddRoundKey.py'],language='c++'),
Extension('SBox',['GeneralizedRijndael/SBox.py'],language='c++'),
Extension('RoundConstant',['GeneralizedRijndael/RoundConstant.py'],
          language='c++'),
Extension('ThirdLevel',['GeneralizedRijndael/ThirdLevel.py'],language='c++'),
]

shortDescription = "Generalization of the rijndael for "\
                   "academic cryptographic purposes"
longDescription = \
'''This is just a probe of concept. You MUST NOT use this code in production 
projects.

The original schema of the Rijndael cryptosystem has one block size with 5 key 
lenghts. During the AES contest process this was restricted to 3 known key 
lenght sizes: 128, 192 and 256 bits (discating the options for 160 and 224). 
But the parameters flexibility of this schema allows even more posibilities.

The code has been made to academic cryptographic purposes and its 
cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been 
demonstrated its properties like the original Rijndael has. The side-channel 
attacks neither wasn't studied yet, then they are not prevented in the current 
code stage.
'''

configuration = {'name':'GeneralizedRijndael',
                 'version':'%d.%d.%d-%d'
                            %(MAJOR_VERSION,MINOR_VERSION,
                              BUILD_VERSION,REVISION_VERSION),
                 'license':'GPLv3+',
                 'description': shortDescription,
                 'long_description':longDescription,
                 'author':"Sergi Blanch-Torn\'e",
                 'author_email':"sblanch@alumnes.udl.cat",
                 'ext_modules': extensions,
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
