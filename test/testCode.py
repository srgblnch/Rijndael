#!/usr/bin/env python

##############################################################################
##
## file: testCode.py
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

from armor import Armor32,Armor36
from GeneralizedRijndael import GeneralizedRijndael
from random import randint
from optparse import OptionParser

OFERT_BITS = 17#bits => up to 131071
BONO_BITS = 16#bits => up to 65535
ATTR_BITS = 7#its => up to 128

##option 64 bits block
#CRC_BITS = 24
#ROUNDS = 40
#ROWS = 2
#COLUMNS = 4
#WORDSIZE = 8
#KCOLUMNS = 8

##option 56 bits block
#CRC_BITS = 16
#ROUNDS = 40
#ROWS = 4
#COLUMNS = 7
#WORDSIZE = 2
#KCOLUMNS = 16

#option 48 bits block
CRC_BITS = 8
ROUNDS = 40
ROWS = 2
COLUMNS = 3
WORDSIZE = 8
KCOLUMNS = 8

NLOOPS = 10000

class BarCode:
    def __init__(self,key,debug=False):
        self.__debug=debug
        self.__armor32 = Armor32()
        self.__biggest32 = len(self.__armor32.encode((2**(ROWS*COLUMNS*WORDSIZE))-1))
        self.__armor36 = Armor36()
        self.__biggest36 = len(self.__armor36.encode((2**(ROWS*COLUMNS*WORDSIZE))-1))
        self.__rijndael = GeneralizedRijndael(key=int(key),
                                              nRounds=ROUNDS,
                                              nRows=ROWS,nColumns=COLUMNS,
                                              wordSize=WORDSIZE,
                                              nKeyWords=KCOLUMNS,
                                              debug=debug)
        self._crc = None
    def generateCode(self,nOfert,nBonus,attributes):
        plain = ((((nOfert << BONO_BITS)|nBonus) << ATTR_BITS)|attributes)
        crc = self.crc(plain,CRC_BITS)
        plain <<= CRC_BITS
        plain |= crc
        code = self.__rijndael.cipher(plain)
        code36 = self.__armor36.encode(code)
        while len(code36) < self.__biggest36:
            code36 = "0%s"%code36
        return code36
    def validateCode(self,code):
        code = self.__armor36.decode(code)
        plain = self.__rijndael.decipher(code)
        crcMask = int('0b'+('1'*CRC_BITS),2)
        crc = plain&crcMask
        plain >>= CRC_BITS
        if not crc == self.crc(plain,CRC_BITS):
            raise Exception("Invalid code","%d != %d"%(crc,self.crc(plain,CRC_BITS)))
        attrMask = int('0b'+('1'*ATTR_BITS),2)
        attrs = plain&attrMask
        plain = plain >> ATTR_BITS
        nBonusMask = int('0b'+('1'*BONO_BITS),2)
        nBonus = plain&nBonusMask
        plain = plain >> BONO_BITS
        nOfertMask = int('0b'+('1'*OFERT_BITS),2)
        nOfert = plain&nOfertMask
        plain = plain>>OFERT_BITS
        return [nOfert,nBonus,attrs]
    def crc(self,data,outlen):
        #TODO:...
        crc = 0
        mask = int('0b'+('1'*outlen),2)
        while data != 0:
            crc ^= data&mask
            data = data >> outlen
        self._crc = crc
        return crc
    def getcrc(self):
        return self._crc

def convertKey(keystr):
    if keystr[:2] == '0x':
        return int(keystr,16)
    else:
        return int(keystr)

def generateAndValidateLoop(nloops=NLOOPS,debug=False):
    kbits = KCOLUMNS*ROWS*WORDSIZE
    errors = 0
    codeLenghts = {}
    for i in range(nloops):
        try:
            err = 0
            #generate codeslenght
            key = randint(0,int('0b'+'1'*(kbits),2))
            tester = BarCode(int(key),debug)
            ofert = randint(0,131071)
            bonus = randint(0,65535)
            attrs = randint(0,127)
            #FIXME: may exclude if the joints of values has been already tested
            code = tester.generateCode(ofert,bonus,attrs)
            print("Ofert: %s\tBonus:%s\twith attrs:%s\tkey:%s\tcrc:%s\n"\
                  "The code is %s (base36)(len %d)"
                  %(ofert,bonus,attrs,hex(key),hex(tester.getcrc()),code.upper(),len(code)))
            if not codeLenghts.has_key(len(code)): codeLenghts[len(code)] = 0
            codeLenghts[len(code)] +=1            
            #validates this codes        
            try:
                r = tester.validateCode(code)
            except Exception,e:
                err +=1
                print("Validation exception: %s"%(e))
            else:
                if ofert==r[0] and bonus == r[1] and attrs == r[2]:
                    print("Well done! code %s (base36) match with "\
                          "ofert %d,bonus %d, attrs %d, crc %s"
                          %(code.upper(),r[0],r[1],r[2],hex(tester.getcrc())))
            if not err == 0: errors += 1
            print("\n")
        except: break
    if not errors == 0:
        print("\n--There where %d errors!--\n"%(errors))
    else:
        print("\n--No errors found--\n")
    for lenght in codeLenghts.keys():
        print("Base 36 have had %d codes with lenght %d\n"%(codeLenghts[lenght],lenght))

def main():#arg0,arg1,arg2):
    parser = OptionParser()
    
    parser.add_option("-g","--generate",
                      help="Used to generate codes giving 3 integer arguments (O..O,B..B,A..A)\n"\
                           "max Ofert=131071,bonus=65535,attr=128")
    parser.add_option("-v", "--validate",
                      help="Used to validate a given code")
    parser.add_option("-k","--key",
                      help="Hexadecimal value of the key")
    parser.add_option("-d", "--debug",
                      help="Set debug mode",default=False)
    
    parser.add_option("-l","--loop",
                      help="Test the ticket system with in a loop of random values")#,default=NLOOPS)
    
    (options, args) = parser.parse_args()
    print options
    debug = options.debug
    
    if not options.loop:
        if not options.key:
            print("\n\tImpossible to work without \"key\" parameter\n")
            exit(-1)
        if not options.generate and not options.validate:
            print("\n\tImpossible to work without one of the \"generate\" or \"validate\" options\n")
            exit(-2)
        key = convertKey(options.key)
        if options.generate:
            generator = BarCode(int(key),options.debug)
            ofert,bonus,attrs = options.generate.split(",")
            code = generator.generateCode(int(ofert), int(bonus), int(attrs))
            print("\nFor Ofert: %s\tBonus:%s\twith attrs:%s (crc %s)\n\t"\
                  "The code is %s (base36)(len %d)"
                  %(ofert,bonus,attrs,hex(generator.getcrc()),code.upper(),len(code)))
        else:
            validator = BarCode(int(key),options.debug)
            code = options.validate
            try:
                r = validator.validateCode(code)
            except Exception,e:
                print("Validation exception: %s"%(e))
            else:
                nOfert,nBonus,attrs = r
                print("Valid: ofert: %d, bonus: %d, attributes: %d, crc: %s\n"
                      %(nOfert,nBonus,attrs,hex(validator.getcrc())))
    else:
        generateAndValidateLoop(int(options.loop),options.debug)

if __name__ == "__main__":
    main()
