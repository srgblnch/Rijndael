#!/usr/bin/env python

##############################################################################
##
## file: rijndael32Test.py
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

from GeneralizedRijndael import GeneralizedRijndael,Logger

def rijndael32_32key_228(debug=False):
    plainText = 0x00112233
    cipherKey = 0x00010203
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=10,nRows=2,nColumns=2,wordSize=8,nKeyWords=2,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        Logger().debug_stream("should be", plainText)

def rijndael32_32key_442(debug=False):
    plainText = 0x00112233
    cipherKey = 0x00010203
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=10,nRows=4,nColumns=4,wordSize=2,nKeyWords=4,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_48key_228(debug=False):
    plainText = 0x00112233
    cipherKey = 0x000102030405
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=12,nRows=2,nColumns=2,wordSize=8,nKeyWords=3,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_48key_442(debug=False):
    plainText = 0x00112233
    cipherKey = 0x000102030405
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=12,nRows=4,nColumns=4,wordSize=2,nKeyWords=6,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_64key_228(debug=False):
    plainText = 0x00112233
    cipherKey = 0x0001020304050607
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=14,nRows=2,nColumns=2,wordSize=8,nKeyWords=4,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_64key_442(debug=False):
    plainText = 0x00112233
    cipherKey = 0x0001020304050607
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=14,nRows=4,nColumns=4,wordSize=2,nKeyWords=8,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_128key_228(debug=False):
    plainText = 0x00112233
    cipherKey = 0x00010203040506070809101112131415
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=16,nRows=2,nColumns=2,wordSize=8,nKeyWords=8,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_128key_442(debug=False):
    plainText = 0x00112233
    cipherKey = 0x00010203040506070809101112131415
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=16,nRows=4,nColumns=4,wordSize=2,nKeyWords=16,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        debug_stream("should be", plainText)

def rijndael32_128key_loop(n):
    from random import randint
    for i in range(n):
        plain = randint(0,0xFFFFFFFF)
        key = randint(0,0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        rijndael32_442 = GeneralizedRijndael(key,nRounds=16,nRows=4,nColumns=4,wordSize=2,nKeyWords=16)
        rijndael32_228 = GeneralizedRijndael(key,nRounds=16,nRows=2,nColumns=2,wordSize=8,nKeyWords=8)
        cipher_442 = rijndael32_442.cipher(plain)
        cipher_228 = rijndael32_228.cipher(plain)
        plain_442 = rijndael32_442.decipher(cipher_442)
        plain_228 = rijndael32_228.decipher(cipher_228)
        print("%4d:   plain %10s key %34s:\n\t442: cipher %10s plain %10s\n\t228: cipher %10s plain %10s"
              %(i,hex(plain),hex(key),hex(cipher_442),hex(plain_442),hex(cipher_228),hex(plain_228)))
        if not plain == plain_442 == plain_228: break

if __name__ == "__main__":
    #---- TODO: cmdline arguments
    #           - which of the tests to be called
    #           - debug mode
    rijndael32_32key_228(True)
    rijndael32_32key_442(True)
    
    rijndael32_48key_228()
    rijndael32_48key_442()
    
    rijndael32_64key_228()
    rijndael32_64key_442()
    
    rijndael32_128key_228()
    rijndael32_128key_442()
    
    rijndael32_128key_loop(100)
    