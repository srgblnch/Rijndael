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
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2015 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

from copy import deepcopy as _deepcopy
from Logger import Logger as _Logger
from SBox import SBox


class SubBytes(_Logger):
    '''This class is made to do the subBytes Rijndael's non-linear
       substitution to provide confusion to the ciphertext, and its inverse.
       It uses a secondary object SBox as a builder pattern to allow the
       transformation from this operation.
       FIXME: The precalculated SBoxes shall be replaced by the calculations
       themselves specially to allow arbitrary word sizes and not only the
       original 8 bits and the two included here for 2 and 4 bits.
    '''
    def __init__(self, wordSize, sboxCalc=False, loglevel=_Logger._info,
                 *args, **kwargs):
        super(SubBytes, self).__init__(*args, **kwargs)
        self.__sbox = SBox(wordSize, useCalc=sboxCalc, loglevel=loglevel)

    @property
    def Field(self):
        return _deepcopy(self.__sbox.getField())

    @property
    def Ring(self):
        return _deepcopy(self.__sbox.getRing())

    @property
    def Mu(self):
        return _deepcopy(self.__sbox.getMu())

    @property
    def Nu(self):
        return _deepcopy(self.__sbox.getNu())

    def do(self, input):
        return self.__sbox.transform(input)

    def invert(self, input):
        return self.__sbox.transform(input, invert=True)
        # It's the same but different sbox
