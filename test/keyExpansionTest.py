#!/usr/bin/env python

##############################################################################
##
## file: keyExpansionTest.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2011, 2012, 2013, 2014 (copyleft)
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

from GeneralizedRijndael import KeyExpander

def keyExpansionTest(rounds,rows,columns,wordSize,kColumns=0,debug=False):
    from random import randint
    if kColumns == 0: kColumns = columns
    kbits = kColumns*rows*wordSize
    key = randint(0,int('0b'+'1'*(kbits),2))
    print("key %s"%hex(key))
    keyExpander = KeyExpander(key,rounds,rows,columns,wordSize,kColumns,debug)
    print("expanded key %s"%keyExpander.getKey())

if __name__ == "__main__":
    #---- TODO: cmd params to change this settings
    #           - debug flag on cmd line
    keyExpansionTest(10,4,4,8,4)
    keyExpansionTest(10,4,4,8,6)
    keyExpansionTest(10,4,4,8,8)

