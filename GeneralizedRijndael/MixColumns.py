#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: MixColumns.py
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

from copy import deepcopy as _deepcopy
from Logger import Logger as _Logger
from Polynomials import PolynomialRing as _PolynomialRing
from Polynomials import getBinaryPolynomialFieldModulo \
                    as _getBinaryPolynomialFieldModulo
from Polynomials import TwoVblePolynomialModulo as _TwoVblePolynomialModulo
from Polynomials import BinaryPolynomialModulo as _BinaryPolynomialModulo

class MixColumns(_Logger):
    def __init__(self,nRows,nColumns,wordSize,loglevel=_Logger._info):
        _Logger.__init__(self,loglevel)
        #---- FIXME: refactor this horrible if
        if wordSize==8:
            polynomialModule=_getBinaryPolynomialFieldModulo(wordSize)
            self._subfield = _BinaryPolynomialModulo(polynomialModule)
            if nRows==4:
                #MDS matrices (Maximum Distance Separable)
                self.__c=[0x3,0x1,0x1,0x2]
                self.__d=[0xB,0xD,0x9,0xE]#c(x) \otimes d(x) = 1 (mod m)
                self._ring = _TwoVblePolynomialModulo("x^4+1",self._subfield)
            elif nRows==3:
                self.__c=[0xD,0x1,0x1]#---- FIXME: unknown
                self.__d=[0x3C,0xAA,0x3C]#---- FIXME: unknown
                self._ring = _TwoVblePolynomialModulo("x^3+1",self._subfield)
            elif nRows==2:
                self.__c=[0x2,0x3]#---- FIXME: unknown
                self.__d=[0x2,0x3]#---- FIXME: unknown
                self._ring = _TwoVblePolynomialModulo("x^2+1",self._subfield)
        else:
            raise Exception("(__init__)","There is no MixColumns for %d "\
                            "wordsize"%(self.__wordSize))
        self.__cx = self._ring([self._subfield(i) for i in self.__c])
        self.__dx = self._ring([self._subfield(i) for i in self.__d])
        self._nColumns = nColumns
        self.__polynomialRing=_PolynomialRing(nRows,nColumns,wordSize)

    def do(self,input):
        self._info_stream("input: %s"%(printlist(input)))
        #First do with the first approach made
        res = self.__polynomialRing.product(self.__c,input)
        #Second way with a class that implements a polynomial ring
        #with coeficients in a binary polynomial field.
        nRows = len(input)
        output = [[self._subfield(input[r][c]) for r in range(nRows)] \
                                      for c in range(self._nColumns)]
        for c in range(self._nColumns):
            self._info_stream("For column %d"%(c))
            sx = self._ring([self._subfield(input[r][c]) \
                             for r in range(len(input))])
            sx_ = self.__cx * sx
            self._info_stream("\t%s * %s"%(hex(self.__cx),hex(sx)))
            self._info_stream("\t\t= %s"%(hex(sx_)))
#             self._info_stream("\t%s * %s"%((self.__cx,sx)))
#             self._info_stream("\t\t= %s"%(sx_))
            for r in range(self._nColumns):
                self._info_stream("output[%d][%d] %s += %s : %s += %s"
                                  %(r,c,hex(output[r][c]),
                                    hex(sx_.coefficients[r]),output[r][c],
                                    sx_.coefficients[r]))
                output[r][c] += sx_.coefficients[-r]
        for c in range(self._nColumns):
            for r in range(nRows):
                output[r][c] = output[r][c].coefficients
        self._info_stream("output: %s"%(printlist(output)))
        if res == output:
            return res
        self._error_stream("\nFailed\tinput:\t%s\n\tres:\t%s\n\toutput\t%s"
                        %(printlist(input),printlist(res),printlist(output)))

    def invert(self,input):
        res = self.__polynomialRing.product(self.__d,input)
        return res

def printlist(l):
    if type(l) == list:
        ans = "["
        for i,e in enumerate(l):
            ans += "%s"%(printlist(e))
            if i != len(l)-1:
                ans += ","
        return ans + "]"
    else:
        return "0x%X"%(l)

def main():
    input = [[randint(0,2**8) for i in range(4)] for j in range(4)]
    mc = MixColumns(4,4,8)
    mc.do(input)


if __name__ == "__main__":
    from random import randint
    main()
