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

from GeneralizedRijndael import GeneralizedRijndael
from optparse import OptionParser
from random import randint

def rijndaelAny(rounds,rows,columns,wordSize,kColumns=0,debug=False):
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
    nbits = columns*rows*wordSize
    plain = randint(0,int('0b'+'1'*(nbits),2))
    cipher = rijndael.cipher(plain)
    plainbis = rijndael.decipher(cipher)
    print("(%dx%d) (w=%d,nbits=%d): %s ?= %s"
          %(rows,columns,wordSize,nbits,hex(plain),hex(plainbis)))
    if plain == plainbis: print "Test OK"
    else: print "Agh!"

def rijndael_allowedBlocks():
    results = {}
    for columns in range(2,10):
        for rows in [2,3,4]:
            for wordSize in [2,4,8]:
                for kcolumns in range(columns,columns+11):
                    for rounds in range(10,20):
                        kbits = kcolumns*rows*wordSize
                        key = randint(0,int('0b'+'1'*(kbits),2))
                        rijndael = GeneralizedRijndael(key,
                                                        nRounds=rounds,
                                                        nRows=rows,
                                                        nColumns=columns,
                                                        wordSize=wordSize,
                                                        nKeyWords=kcolumns)
                        nbits = columns*rows*wordSize
                        plain = randint(0,int('0b'+'1'*(nbits),2))
                        cipher = rijndael.cipher(plain)
                        plainbis = rijndael.decipher(cipher)
                        print("(%dx%d) (w=%d,nbits=%d): %s ?= %s"
                              %(rows,columns,wordSize,nbits,hex(plain),hex(plainbis)))
                        if not results.has_key(nbits):
                            results[nbits] = {}
                        if not results[nbits].has_key(kbits):
                            results[nbits][kbits] = []
                        if plain == plainbis:
                            results[nbits][kbits].append([rounds,rows,columns,wordSize,kcolumns,True])
                            print "Test OK\n"
                        else:
                            results[nbits][kbits].append([rounds,rows,columns,wordSize,kcolumns,False])
                            print "Agh!\n"
    bits2sort = results.keys()
    bits2sort.sort()
    for nbits in bits2sort:
        keys2sort = results[nbits].keys()
        keys2sort.sort()
        for kbits in keys2sort:
            print("%4dbits with %4dkey:"%(nbits,kbits))
            for testElement in results[nbits][kbits]:
                print("\t%s"%(testElement))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a","--all",
                      help="Loop in \"all\" the sizes under study")
    parser.add_option("-s", "--sizes",type="string",
                      help="Coma separated of the Rijndael parameters", metavar="SIZES")
    parser.add_option("-d", "--debug",
                      help="Set debug mode",default=False)
    #---- TODO: allow different debugs
    
    (options, args) = parser.parse_args()
    debug = options.debug
    
    print options.all
    
    if not options.all == None:
        sizes = options.sizes.split(',')
        if len(sizes) in [4,5]:
            rounds = int(sizes[0])
            rows = int(sizes[1])
            columns = int(sizes[2])
            wordSize = int(sizes[3])
            if len(sizes) == 5:
                kColumns = int(sizes[4])
                rijndaelAny(rounds,rows,columns,wordSize,kColumns,debug=debug)
            else:
                rijndaelAny(rounds,rows,columns,wordSize,debug=debug)
    else:
        rijndael_allowedBlocks()
    
    