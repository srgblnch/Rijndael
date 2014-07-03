#!/usr/bin/env python

##############################################################################
##
## file: timeitTest.py
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

import timeit
import time
import platform
import json

def test(rows,columns,wordsize,kColumns):
    return '''
        from GeneralizedRijndael import GeneralizedRijndael
        from random import randint
        rows,columns,wordSize = %d,%d,%d
        kColumns = %d
        kbits = kColumns*rows*wordSize
        rounds = max(columns,kColumns) + 6
        rijndael = GeneralizedRijndael(key=randint(0,int(2**kbits)-1),
                                      nRounds=rounds,
                                      nRows=rows,
                                      nColumns=columns,
                                      wordSize=wordSize,
                                      nKeyWords=kColumns)
        nbits = columns*rows*wordSize
        plain = randint(0,int(2**nbits)-1)
        cipher = rijndael.cipher(plain)
        plainbis = rijndael.decipher(cipher)
        '''%(rows,columns,wordsize,kColumns)

results = {}
repeat = 10
number = 10000
try:
    for columns in range(2,10):
        for rows in [2,3,4]:
            for wordSize in [2,4,8]:
                block_bits = rows*columns*wordSize
                block_desc = "%s"%str((rows,columns,wordSize))
                if not results.has_key(block_bits):
                    results[block_bits] = {}
                if not results[block_bits].has_key(block_desc):
                    results[block_bits][block_desc] = {}
                for kcolumns in range(columns,columns+11):
                    key_bits = rows*kcolumns*wordSize
                    key_desc = "%s"%str((rows,kcolumns,wordSize))
                    if not results[block_bits][block_desc].has_key(key_bits):
                        results[block_bits][block_desc][key_bits] = {}
                    timesets = timeit.Timer(test(rows,
                                                 columns,
                                                 wordSize,
                                                 kcolumns)).repeat(repeat,number)
                    results[block_bits][block_desc]\
                           [key_bits][key_desc] = timesets
                    print("For %d bits block (%d,%d,%d) and "\
                          "%d bits key (%d,%d,%d): %s"
                          %(block_bits,rows,columns,wordSize,
                            key_bits,rows,kcolumns,wordSize,
                            timesets))
except Exceptio,e:
    print("Uou! %s"%(e))
filename = '%s_rijndael_timeittest'%(time.strftime("%Y%m%d_%H%M%S"))
with open(filename,'w') as file:
    file.write('#System: %s (%s)\n'%(platform.system(),platform.release()))
    file.write('#Arch: %s\n'%(str(platform.architecture())))
    file.write('#repeat %d, number %d'%(repeat,number))
    file.write(json.dumps(results, sort_keys=True,
                          indent=4, separators=(',', ': ')))

