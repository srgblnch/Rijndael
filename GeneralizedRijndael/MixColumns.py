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

from Logger import Logger
from Polynomials import PolynomialRing,getBinaryPolynomialFieldModulo,\
                        BinaryPolynomialModulo

class MixColumns(Logger):
    def __init__(self,nRows,nColumns,wordSize,loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        #---- FIXME: refactor this horrible if
        if wordSize==8:
            if nRows==4:
                #MDS matrices (Maximum Distance Separable)
                self.__cx=[0x3,0x1,0x1,0x2]
                self.__dx=[0xB,0xD,0x9,0xE]#c(x) \otimes d(x) = 1 (mod m)
            elif nRows==3:
                self.__cx=[0xD,0x1,0x1]#---- FIXME: unknown
                self.__dx=[0x3C,0xAA,0x3C]#---- FIXME: unknown
            elif nRows==2:
                self.__cx=[0x2,0x3]#---- FIXME: unknown
                self.__dx=[0x2,0x3]#---- FIXME: unknown
            polynomialModule=getBinaryPolynomialFieldModulo(wordSize)#0b100011011
#        elif  wordSize==4:
#            if nRows==4:
#                self.__cx=self.__dx=[0,0,0,0]#---- FIXME: unknown
#            elif nRows==3:
#                self.__cx=self.__dx=[0,0,0]#---- FIXME: unknown
#            elif nRows==2:
#                self.__cx=self.__dx=[0,0]#---- FIXME: unknown
#            polynomialModule=0b10000
#        elif  wordSize==2:
#            if nRows==4:
#                self.__cx=self.__dx=[0x3,0x1,0x1,0x2]#---- FIXME: unknown
#            elif nRows==3:
#                self.__cx=self.__dx=[0,0,0]#---- FIXME: unknown
#            elif nRows==2:
#                self.__cx=self.__dx=[0x2,0x3]#---- FIXME: unknown
#            polynomialModule=0b100
        else:
            raise Exception("(__init__)","There is no MixColumns for %d "\
                            "wordsize"%(self.__wordSize))
        self.__polynomialRing=PolynomialRing(nRows,nColumns,wordSize)
    def do(self,input):
        return self.__polynomialRing.product(self.__cx,input)
    def invert(self,input):
        return self.__polynomialRing.product(self.__dx,input)
