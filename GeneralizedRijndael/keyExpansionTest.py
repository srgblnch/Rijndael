#!/usr/bin/env python

##############################################################################
##
## file: keyExpansionTest.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2011, 2012 (copyleft)
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

from GeneralizedRijndael import GeneralizedRijndael

def keyExpansionTest(rounds,rows,columns,wordSize,kColumns=0,debug=True):
    from random import randint
    if kColumns == 0: kColumns = columns
    kbits = kColumns*rows*wordSize
    key = randint(0,int('0b'+'1'*(kbits),2))
    rijndael = GeneralizedRijndael(key,
                                    nRounds=rounds,
                                    nRows=rows,
                                    nColumns=columns,
                                    wordSize=wordSize,
                                    nKeyWords=kColumns,
                                    debug=debug)

if __name__ == "__main__":
    #---- TODO: cmd params to change this settings
    #           - debug flag on cmd line
    keyExpansionTest(10,4,4,8,4)