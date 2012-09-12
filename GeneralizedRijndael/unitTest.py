#!/usr/bin/env python

##############################################################################
##
## file: unitTest.py
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

def unitTest(debug=False):
    #plainText = 0x3243F6A8885A308D313198A2E0370734
    cipherKey = 0x2B7E151628AED2A6ABF7158809CF4F3C
    srv = GeneralizedRijndael(cipherKey,debug=debug)
    
    print("\nTest the addRoundKey() method")
    state=[[0x32,0x88,0x31,0xe0],
           [0x43,0x5a,0x31,0x37],
           [0xf6,0x30,0x98,0x07],
           [0xa8,0x8d,0xa2,0x34]]
    subkey=[0x2b7e1516,0x28aed2a6,0xabf71588,0x09cf4f3c]
    srv.debug("state",state,0,"cipher->addRoundKey()\t")
    srv.debug("subkey",subkey,0,"cipher->addRoundKey()\t")
    srv._addRoundKey(state,subkey)
    srv.debug("state",state,0,"cipher->addRoundKey()\t")
    unit = [[0x19,0xa0,0x9a,0xe9],
            [0x3d,0xf4,0xc6,0xf8],
            [0xe3,0xe2,0x8d,0x48],
            [0xbe,0x2b,0x2a,0x08]]
    unitTest = srv.unitTestCompare(state,unit)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("state", unit,operation="should be\t\t\t")

    print("\nTest the subBytes() method")
    state = [[0x19,0xa0,0x9a,0xe9],
             [0x3d,0xf4,0xc6,0xf8],
             [0xe3,0xe2,0x8d,0x48],
             [0xbe,0x2b,0x2a,0x08]]
    srv.debug("state",state,0,"cipher->subBytes()\t")
    srv._subBytes(state)
    srv.debug("state",state,0,"cipher->subBytes()\t")
    unit = [[0xd4,0xe0,0xb8,0x1e],
            [0x27,0xbf,0xb4,0x41],
            [0x11,0x98,0x5d,0x52],
            [0xae,0xf1,0xe5,0x30]]
    unitTest = srv.unitTestCompare(state,unit)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("state", unit,operation="should be\t\t\t")

    print("\nTest the shiftRows() method")
    state = [[0xd4,0xe0,0xb8,0x1e],
             [0x27,0xbf,0xb4,0x41],
             [0x11,0x98,0x5d,0x52],
             [0xae,0xf1,0xe5,0x30]]
    srv.debug("state",state,0,"cipher->shiftRows()\t")
    state = srv._shiftRows(state)
    srv.debug("state",state,0,"cipher->shiftRows()\t")
    unit = [[0xd4,0xe0,0xb8,0x1e],
            [0xbf,0xb4,0x41,0x27],
            [0x5d,0x52,0x11,0x98],
            [0x30,0xae,0xf1,0xe5]]
    unitTest = srv.unitTestCompare(state,unit)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("state", unit,operation="should be\t\t\t")

    print("\nTest the MixColumns() method")
    state = [[0xd4,0xe0,0xb8,0x1e],
             [0xbf,0xb4,0x41,0x27],
             [0x5d,0x52,0x11,0x98],
             [0x30,0xae,0xf1,0xe5]]
    srv.debug("state",state,0,"cipher->MixColumns()\t")
    state = srv._mixColumns(state)
    srv.debug("state",state,0,"cipher->MixColumns()\t")
    unit = [[0x04,0xe0,0x48,0x28],
            [0x66,0xcb,0xf8,0x06],
            [0x81,0x19,0xd3,0x26],
            [0xe5,0x9a,0x7a,0x4c]]
    unitTest = srv.unitTestCompare(state,unit)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("state", unit,operation="should be\t\t\t")


if __name__ == "__main__":
    unitTest()