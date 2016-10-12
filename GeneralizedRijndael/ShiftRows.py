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

from Logger import Logger as _Logger
from ThirdLevel import shift as _shift


class ShiftRows(_Logger):
    def __init__(self, nRows, *args, **kwargs):
        super(ShiftRows, self).__init__(*args, **kwargs)
        self.__nRows = nRows

    def __str__(self):
        parentesis = "%d" % (self.__nRows)
        return "ShiftRows(%s)" % (parentesis)

    def __repr__(self):
        return "%s" % (self.__str__())
    def do(self, input):
        '''One of the round transformation methods.
           cyclical left shift of the row 'i' of the state matrix by 'i'
           positions s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output = []
        for i in range(self.__nRows):
            shifted = _shift(input[i], i)
            self._debug_stream("row[%d] = %s -> %s" % (i, input[i], shifted),
                               operation="shiftRows")
            output.append(shifted)
        return output

    def invert(self, input):
        '''Inverse of the shiftRows() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output = []
        for i in range(self.__nRows):
            unshifted = _shift(input[i], -i)
            self._debug_stream("row[%d] = %s -> %s" % (i, input[i], unshifted),
                               operation="invShiftRows")
            output.append(unshifted)
        return output
