#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: AddRoundKey.py
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
from ThirdLevel import Word

class AddRoundKey(Logger):
    def __init__(self,nRows,nColumns,wordSize,loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__word=Word(nRows,wordSize)
    def do(self,input,subkey):
        '''One of the round transformation methods.
           The round key (from the PRG) list of arrays (can be thougth as a
           matrix), is bitwise XORted with the state matrix.
           Input: <integer arrays> state, subkey
           Output: <integer arrays> state (modified)
        '''
        output=input
        for j in range(self.__nColumns):
            byteSubkey=self.__word.toList(subkey[j])
            byteSubkey.reverse()
            for i in range(self.__nRows):
                bar=output[i][j]
                bar^=byteSubkey[i]
                output[i][j]=bar
        return output