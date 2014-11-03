#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: KeyExpansion.pyx
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

import Logger

class KeyExpansion(Logger.Logger):
    def __init__(self,key,
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None,
                 loglevel=Logger.Logger.info):
        Logger.Logger.__init__(self,loglevel)
        self.__key=key
        self.__nRounds=nRounds
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__wordSize=wordSize
        self.__nKeyWords=nKeyWords
        #self.__sbox=SBox(wordSize)
        #self.__word=Word(nRows,wordSize)
        self.__keyExpanded=[None]*self.__nKeyWords
        self.debug_stream("key",key,operation="keyExpansion()\t")
        