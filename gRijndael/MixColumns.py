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
from Polynomials import BinaryExtensionModulo as _BinaryExtensionModulo
from Polynomials import getBinaryExtensionFieldModulo \
    as _getBinaryExtensionFieldModulo
from Polynomials import getPolynomialRingWithBinaryCoefficients \
    as _getPolynomialRingWithBinaryCoefficients
from Polynomials import PolynomialRing as _PolynomialRing
from Polynomials import PolynomialRingModulo as _PolynomialRingModulo


class MixColumns(_Logger):
    """
        Object in charge of the MixColumns operation:
        Parameters:
        - nRows
        - nColumns
        - wordSize
    """
    def __init__(self, nRows, nColumns, wordSize,
                 *args, **kwargs):
        super(MixColumns, self).__init__(*args, **kwargs)
        self.__nRows = nRows
        self.__nColumns = nColumns
        self.__wordSize = wordSize
        if (2 <= self.__nRows <= 16) and (2 <= self.__wordSize <= 16):
            self.__cx, self.__ring, self.__field = \
                _getPolynomialRingWithBinaryCoefficients(self.__nRows,
                                                         self.__wordSize)
            self.__dx = ~self.__cx
        else:
            raise Exception("(__init__)", "There is no MixColumns for the pair"
                            " %d degree ring (number of rows) "
                            "with %d degree coefficients (word size)"
                            % (self.__nRows, self.__wordSize))

    def __str__(self):
        parentesis = "%d, %d, %d" % (self.__nRows, self.__nColumns,
                                     self.__wordSize)
        return "MixColumns(%s)" % (parentesis)

    def __repr__(self):
        return "%s" % (self.__str__())

    @property
    def PolynomialRingModulo(self):
        return _deepcopy(self.__cx.modulo)

    @property
    def SubfieldModulo(self):
        return _deepcopy(self.__cx._coefficients[0].modulo)

    @property
    def Cx(self):
        return hex(self.__cx)

    @property
    def Dx(self):
        return hex(self.__dx)

    def do(self, input):
        return self.__product(input, self.__cx, operation="mixColumns")

    def invert(self, input):
        return self.__product(input, self.__dx, operation="InvMixColumns")

    def __product(self, input, polynomial, operation):
        self._debug_stream("input: %s" % (printlist(input)),
                           operation=operation)
        nRows = len(input)
        # take the columns, convert each element to a binary polynomial
        columns = self.__matrix2Polynomials(input)
        self._debug_stream("input as field elements: %s" % (columns),
                           operation=operation)
        self._debug_stream("s'[i] = %s * s[i]" % (polynomial),
                           operation=operation)
        for i, column in enumerate(columns):
            sx = polynomial * column
            self._debug_stream("s[%d] = c(x) * %s = %s" % (i, column, sx),
                               operation=operation)
            columns[i] = sx
        self._debug_stream("output as field elements: %s" % (columns),
                           operation=operation)
        output = self._polynomials2matrix(columns)
        self._debug_stream("output: %s" % (printlist(output)),
                           operation=operation)
        return output

    def __matrix2Polynomials(self, input):
        columns = []
        for c in range(self.__nColumns):
            column = []
            for r in range(self.__nRows):
                column.append(self.__field(input[r][c]))
            # s(r-1,c)*x^(r-1) + s(r-2,c)*x^(r-2) + ... + s(0,c)*x^(r-r)
            columns.append(self.__ring(column))
        return columns

    def _polynomials2matrix(self, input):
        # FIXME: this undo the __matrix2Polynomials(), but can it be optimized?
        matrix = []
        for r in range(self.__nRows):
            matrix.append([])
            for c in range(self.__nColumns):
                matrix[r].append(None)
        for c, column in enumerate(input):
            column = column.coefficients
            while len(column) < self.__nRows:
                column.append(self.__field(0))
            for r, cell in enumerate(column):
                matrix[r][c] = cell.coefficients
        return matrix


def printlist(l):
    if type(l) == list:
        ans = "["
        for i, e in enumerate(l):
            ans += "%s" % (printlist(e))
            if i != len(l)-1:
                ans += ","
        return ans + "]"
    else:
        return "0x%X" % (l)


def main():
    input = [[randint(0, 2**8) for i in range(4)] for j in range(4)]
    mc = MixColumns(4, 4, 8)
    mc.do(input)


if __name__ == "__main__":
    from random import randint
    main()
