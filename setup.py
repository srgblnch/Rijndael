# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2013 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"


# from Cython.Distutils import build_ext
from gRijndael import version
from setuptools import setup, find_packages


setup(name='gRijndael',
      license="GPLv3+",
      description="Python prove of concept to generalise the rijndael's "
                  "parameters.",
      version=version(),
      author="Sergi Blanch-Torn\'e",
      author_email="srgblnchtrn@protonmail.ch",
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: '
                   'GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: POSIX',
                   # 'Programming Language :: Cython',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: '
                   'Interface Engine/Protocol Translator',
                   'Topic :: Software Development :: Embedded Systems',
                   'Topic :: Software Development :: Libraries :: '
                   'Python Modules',
                   'Topic :: Scientific/Engineering :: Mathematics',
                   'Topic :: Security :: Cryptography',
                   ''],
      packages=find_packages(),
      url="https://github.com/srgblnch/Rijndael",
      # entry_points={'console_scripts': 'gRijndael=gRijndael:Launcher'},
      # build_ext=build_ext
      )

# for the classifiers review see:
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
#
# Development Status :: 1 - Planning
# Development Status :: 2 - Pre-Alpha
# Development Status :: 3 - Alpha
# Development Status :: 4 - Beta
# Development Status :: 5 - Production/Stable

# TODO: cython
##############################################################################
# import sys
# import warnings
# from gRijndael.version import *
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
# Extension('gRijndael',
#           define_macros = [('MAJOR_VERSION',
#                             '%d'%MAJOR_VERSION),
#                            ('MINOR_VERSION',
#                             '%d'%MINOR_VERSION),
#                            ('BUILD_VERSION',
#                             '%d'%BUILD_VERSION),
#                            ('REVISION_VERSION',
#                             '%d'%REVISION_VERSION)
#                            ],
#           sources = [#'gRijndael/*.py',
# #                    'gRijndael/Logger.py',
# #                    'gRijndael/ThirdLevel.py',
# #                    'gRijndael/SBox.py',
# #                    'gRijndael/RoundConstant.py',
# #                    'gRijndael/KeyExpansion.py',
# #                    'gRijndael/SubBytes.py',
# #                    'gRijndael/ShiftRows.py',
# #                    'gRijndael/MixColumns.py',
# #                    'gRijndael/AddRoundKey.py',
#                     'gRijndael/gRijndael.py',
#                     ],
#           language = "c++"),
# Extension('Logger',['gRijndael/Logger.py'],language='c++'),
# Extension('KeyExpansion',
#           ['gRijndael/KeyExpansion.py'],language='c++'),
# Extension('SubBytes',['gRijndael/SubBytes.py'],language='c++'),
# Extension('ShiftRows',['gRijndael/ShiftRows.py'],language='c++'),
# Extension('MixColumns',['gRijndael/MixColumns.py'],language='c++'),
# Extension('AddRoundKey',['gRijndael/AddRoundKey.py'],
#           language='c++'),
# Extension('SBox',['gRijndael/SBox.py'],language='c++'),
# Extension('RoundConstant',['gRijndael/RoundConstant.py'],
#           language='c++'),
# Extension('Polynomials',['gRijndael/Polynomials.py'],
#           language='c++'),
# Extension('ThirdLevel',['gRijndael/ThirdLevel.py'],language='c++'),
# Extension('version',['gRijndael/version.py'],language='c++'),
# ]
#
# shortDescription = "Generalization of the rijndael for "\
#                    "academic cryptographic purposes"
# longDescription = \
# '''This is just a probe of concept. You MUST NOT use this code in production
# projects.
#
# The original schema of the Rijndael cryptosystem has one block size with 5
# key lenghts. During the AES contest process this was restricted to 3 known
# key lenght sizes: 128, 192 and 256 bits (discating the options for 160 and
# 224). But the parameters flexibility of this schema allows even more
# posibilities.
#
# The code has been made to academic cryptographic purposes and its
# cryptoanalysis hasn't start yet. It encrypts and decrypts, but it hasn't been
# demonstrated its properties like the original Rijndael has. The side-channel
# attacks neither wasn't studied yet, then they are not prevented in the
# current code stage.
# '''
#
# configuration = {'name':'gRijndael',
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
#                                    "GNU General Public License v3 or later "\
#                                                                   "(GPLv3+)",
#                                 "Topic :: Security :: Cryptography"],
#                  }
#
# setup(**configuration)
