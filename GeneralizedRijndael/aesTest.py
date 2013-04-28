#!/usr/bin/env python

##############################################################################
##
## file: aesTest.py
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

from GeneralizedRijndael import GeneralizedRijndael,debug_stream

def aes128(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=10,nRows=4,nColumns=4,wordSize=8,nKeyWords=4,
                               debug=debug)
    print("aes128 -> 10 rounds, 4 rows, 4 columns, 8 bit word size, and key with 4 words")
    print("plaintext %s (key %s)"%(hex(plainText),hex(cipherKey)))
    cipherText = srv.cipher(plainText)
    print("cipherText %s"%hex(cipherText))
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def aes192(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f1011121314151617
    srv = GeneralizedRijndael(cipherKey,nRounds=12,nKeyWords=6,
                      debug=debug)
    print("aes192 -> 12 rounds, 4 rows, 4 columns, 8 bit word size, and key with 6 words")
    print("plaintext %s (key %s)"%(hex(plainText),hex(cipherKey)))
    cipherText = srv.cipher(plainText)
    print("cipherText %s"%hex(cipherText))
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def aes256(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=14,nRows=4,nColumns=4,wordSize=8,nKeyWords=8,
                               debug=debug)
    print("aes256 -> 14 rounds, 4 rows, 4 columns, 8 bit word size, and key with 8 words")
    print("plaintext %s (key %s)"%(hex(plainText),hex(cipherKey)))
    cipherText = srv.cipher(plainText)
    print("cipherText %s"%hex(cipherText))
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def cipherExample(debug=False):
    plainText = 0x3243F6A8885A308D313198A2E0370734
    cipherKey = 0x2B7E151628AED2A6ABF7158809CF4F3C
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=10,nRows=4,nColumns=4,wordSize=8,nKeyWords=4,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

if __name__ == "__main__":
    aes128()
    aes192()
    aes256()
    #cipherExample()