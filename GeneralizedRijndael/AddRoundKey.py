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

from Logger import Logger as _Logger
from ThirdLevel import Word as _Word


class AddRoundKey(_Logger):
    def __init__(self, nRows, nColumns, wordSize, *args, **kwargs):
        super(AddRoundKey, self).__init__(*args, **kwargs)
        self.__nRows = nRows
        self.__nColumns = nColumns
        self.__word = _Word(nRows, wordSize)

    def do(self, input, subkey):
        '''One of the round transformation methods.
           The round key (from the PRG) list of arrays (can be thougth as a
           matrix), is bitwise XORted with the state matrix.
           Input: <integer arrays> state, subkey
           Output: <integer arrays> state (modified)
        '''
        output = input[:]
        for j in range(self.__nColumns):
            byteSubkey = self.__word.toList(subkey[j])
            byteSubkey.reverse()
            for i in range(self.__nRows):
                bar = output[i][j]
                bar ^= byteSubkey[i]
                output[i][j] = bar
        return output
