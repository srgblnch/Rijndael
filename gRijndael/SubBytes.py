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
__copyright__ = "Copyright 2013 Sergi Blanch-Torne"
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
    def __init__(self, wordSize, sboxCalc=True, loglevel=_Logger._info,
                 *args, **kwargs):
        super(SubBytes, self).__init__(*args, **kwargs)
        self.__wordSize = wordSize
        self.__sbox = SBox(wordSize, useCalc=sboxCalc, loglevel=loglevel)

    def __str__(self):
        parentesis = "%d" % (self.__wordSize)
        return "MixColumns(%s)" % (parentesis)

    def __repr__(self):
        return "%s Mu=%s, Nu=%s, ring=%s, field=%s" % (self.__str__(), self.Mu,
                                                       self.Nu, self.Ring,
                                                       self.Field)

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

    @property
    def SBox(self):
        return self.__sbox

    def do(self, input):
        output = self.__sbox.transform(input)
        self._debug_stream("%s -> %s" % (input, output), operation="subBytes")
        return output

    def invert(self, input):
        output = self.__sbox.transform(input, invert=True)
        self._debug_stream("%s -> %s" % (input, output),
                           operation="invSubBytes")
        return output
        # It's the same but different sbox
