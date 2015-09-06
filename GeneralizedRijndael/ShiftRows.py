#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: ShiftRows.py
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

from Logger import Logger as _Logger
from ThirdLevel import shift as _shift

class ShiftRows(_Logger):
    def __init__(self,nRows,loglevel=_Logger._info):
        _Logger.__init__(self,loglevel)
        self.__nRows=nRows
    def do(self,input):
        '''One of the round transformation methods.
           cyclical left shift of the row 'i' of the state matrix by 'i' 
           positions s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output=[]
        for i in range(self.__nRows):
            output.append(_shift(input[i],i))
        return output
    def invert(self,input):
        '''Inverse of the shiftRows() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output=[]
        for i in range(self.__nRows):
            output.append(_shift(input[i],-i))
        return output
