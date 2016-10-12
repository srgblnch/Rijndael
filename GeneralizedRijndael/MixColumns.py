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
    def __init__(self, nRows, nColumns, wordSize, *args, **kwargs):
        super(MixColumns, self).__init__(*args, **kwargs)
        if (2 <= nRows < 8) and (2 <= wordSize < 16):
            self.__cx, self.__ring, self.__field = \
                _getPolynomialRingWithBinaryCoefficients(nRows, wordSize)
            self.__dx = ~self.__cx
        else:
            raise Exception("(__init__)", "There is no MixColumns for the pair"
                            " %d degree ring (number of rows) "
                            "with %d degree coefficients (word size)"
                            % (nRows, wordSize))
        self._nColumns = nColumns
        # self.__polynomialRing = _PolynomialRing(nRows, nColumns, wordSize)

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
        return self.__product(input, self.__cx)
    
    def invert(self, input):
        return self.__product(input, self.__dx)

    def __product(self, input, polynomial):
        self._debug_stream("input: %s" % (printlist(input)),
                           operation="mixColumns")
        nRows = len(input)
        # take the columns, convert each element to a binary polynomial
        columns = [[self.__field(input[r][c])
                    for c in range(self._nColumns)]
                   for r in range(nRows)]
        self._debug_stream("s'[i] = %s * s[i]" % self.__cx, operation="mixColumns")
        for i, column in enumerate(columns):
            sx = self.__ring(column)
            sx_ = self.__cx * sx
            self._debug_stream("s[%d] = c(x) * %s = %s" % (i, sx, sx_),
                               operation="mixColumns")
            columns[i] = sx_
        output = [[None]*nRows]*self._nColumns
        for c in range(self._nColumns):
            self._debug_stream("Column %d: %s" % (c, columns[c]))
            coefficients = columns[c].coefficients
            for r in range(nRows):
                self._debug_stream("Row %d: %s" % (r, coefficients))
                output[r][c] = coefficients[r].coefficients
        return output
        
# #         # First do with the first approach made
# #         res = self.__polynomialRing.product(self.__c, input)
# #         self._warning_stream("Using the old calculation method: ", data=res,
# #                              operation="mixColumns")
#         # Second way with a class that implements a polynomial ring
#         # with coeficients in a binary polynomial field.
#         nRows = len(input)
#         output = [[self._subfield(input[r][c])
#                    for c in range(self._nColumns)]
#                   for r in range(nRows)]
#         self._debug_stream("output matrix is %d rows by %d columns (%dx%d)"
#                            % (len(output), len(output[0]), nRows,
#                               self._nColumns),
#                            data=output, operation="mixColumns")
#         for r in range(nRows):
#             sx = self._ring([self._subfield(input[r][c])
#                              for c in range(len(input))])
#             sx_ = self.__cx * sx
#             self._debug_stream("\t%s * %s" % (hex(self.__cx), hex(sx)),
#                                operation="mixColumns")
#             self._debug_stream("\t\t= %s" % (hex(sx_)), operation="mixColumns")
#             for c in range(self._nColumns):
#                 self._debug_stream("output[%d][%d] %s += %s : %s += %s"
#                                    % (r, c, hex(output[r][c]),
#                                       hex(sx_.coefficients[-r]),
#                                       output[r][c], sx_.coefficients[r]),
#                                    operation="mixColumns")
#                 output[r][c] += sx_.coefficients[-r]
#         for c in range(self._nColumns):
#             for r in range(nRows):
#                 output[r][c] = output[r][c].coefficients
#         self._debug_stream("output: %s" % (printlist(output)),
#                            operation="mixColumns")
#         if res != output:
#             self._warning_stream("For input:\t%s\n\told way result say:\t%s\n"
#                                  "\tbut vector space modulo say:\t%s"
#                                  % (printlist(input), printlist(res),
#                                     printlist(output)),
#                                  operation="mixColumns")
#         return res
#         # if return 'output', then the test didn't pass.
#         # But with 'res' it does: the vector space modulo is not working well!
# 
#     def invert(self, input):
#         res = self.__polynomialRing.product(self.__d, input)
#         return res


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
