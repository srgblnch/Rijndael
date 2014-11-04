#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: SubBytes.py
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
from SBox import SBox

class SubBytes(Logger):
    '''This class is made to do the subBytes Rijndael's non-linear 
       substitution to provide confusion to the ciphertext, and its inverse.
       It uses a secondary object SBox as a builder pattern to allow the 
       transformation from this operation.
       FIXME: The precalculated SBoxes shall be replaced by the calculations
       themselves specially to allow arbitrary word sizes and not only the
       original 8 bits and the two included here for 2 and 4 bits.
    '''
    def __init__(self,wordSize,loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        self.__sbox=SBox(wordSize)
    def do(self,input):
        return self.__sbox.transform(input)
    def invert(self,input):
        return self.__sbox.transform(input,invert=True)
        #It's the same but different sbox