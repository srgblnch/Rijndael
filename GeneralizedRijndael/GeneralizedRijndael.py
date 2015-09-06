#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: GeneralizedRijndael.py
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

import sys

from Logger import Logger as _Logger
from Logger import levelFromMeaning as _levelFromMeaning
from KeyExpansion import KeyExpansion as _KeyExpansion
from SubBytes import SubBytes as _SubBytes
from ShiftRows import ShiftRows as _ShiftRows
from MixColumns import MixColumns as _MixColumns
from AddRoundKey import AddRoundKey as _AddRoundKey
from ThirdLevel import Long as _Long
from ThirdLevel import State as _State

from version import *

class GeneralizedRijndael(_Logger):
    '''
        TODO: describe & little howto
    '''
    def __init__(self,key,
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None,sboxCalc=False,
                 loglevel=_Logger._info):
        _Logger.__init__(self,loglevel)
        self.__nRounds=nRounds#Num of encryption rounds {10,12,14}
        self.__nRows=nRows#Num of rows in the rectangular arrangement
        self.__nColumns=nColumns#Num of cols in the rectangular arrangement
        self.__wordSize=wordSize#in bits, AES is 8 bits word
        if nKeyWords==None:
            self.__nKeyWords=nColumns
        else:
            self.__nKeyWords=nKeyWords#Usually {4,6,8}
        self._debug_stream("Initialising GeneralizedRijndael (%d,%d,%d,%d,%d):"\
                          " block=%dbits key=%dbits"
                          %(self.__nRounds,self.__nRows,self.__nColumns,
                            self.__wordSize,self.__nKeyWords,
                            self.__nColumns*self.__nRows*self.__wordSize,
                            self.__nKeyWords*self.__nRows*self.__wordSize))
        self._keyExpander = _KeyExpansion(key,self.__nRounds,self.__nRows,
                                               self.__nColumns,self.__wordSize,
                                                     self.__nKeyWords,
                                                     sboxCalc,loglevel)
        self._subBytes = _SubBytes(wordSize,sboxCalc,loglevel)
        self._shiftRows = _ShiftRows(nRows,loglevel)
        self._mixColumns = _MixColumns(nRows,nColumns,wordSize,loglevel)
        self._addRoundKey = _AddRoundKey(nRows,nColumns,wordSize,loglevel)

    def cipher(self,plain):
        '''plain (1d array) is copied to state matrix.
           After the inicial round addition, the state is transformed by the
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
           Input: <integer> plainText
           Output: <integer> cipherText
        '''
        self._debug_stream("plaintext",plain)
        plain=_Long(self.__wordSize).toArray(plain,self.__nColumns*self.__nRows*\
                                            self.__wordSize)
        #---- TODO: check the plain have the size to be ciphered
        self._debug_stream("plaintext array",plain)
        #---- FIXME: State should be protected in memory 
        #            to avoid side channel attacks
        state=_State(self.__nRows,self.__nColumns,
                    self._logLevel).fromArray(plain)
        self._debug_stream("state",state)
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey(0,self.__nColumns))#w[0,Nb-1]
        self._debug_stream("state",state,0,"cipher->addRoundKey()\t")
        for r in range(1,self.__nRounds):#[1..Nr-1] step 1
            state=self._subBytes.do(state)
            self._debug_stream("state",state,r,"cipher->subBytes()\t")
            state=self._shiftRows.do(state)
            self._debug_stream("state",state,r,"cipher->shiftRows()\t")
            state=self._mixColumns.do(state)
            self._debug_stream("state",state,r,"cipher->mixColumns()\t")
            state=self._addRoundKey.do(state,\
                    self._keyExpander.getSubKey((r*self.__nColumns),
                                                (r+1)*(self.__nColumns)))
            self._debug_stream("state",state,r,"cipher->addRoundKey()\t")
        state=self._subBytes.do(state)
        self._debug_stream("state",state,self.__nRounds,"cipher->subBytes()\t")
        state=self._shiftRows.do(state)
        self._debug_stream("state",state,self.__nRounds,"cipher->shiftRows()\t")
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),
                                            (self.__nRounds+1)*\
                                            (self.__nColumns)))
        self._debug_stream("state",state,
                          self.__nRounds,"cipher->addRoundKey()\t")
        cipher=_State(self.__nRows,self.__nColumns,
                     self._logLevel).toArray(state)
        self._debug_stream("ciphertext array",cipher)
        cipher=_Long(self.__wordSize).fromArray(cipher,self.__nColumns*\
                                               self.__nRows*self.__wordSize)
        self._debug_stream("ciphertext",cipher)
        return cipher

    def decipher(self,cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
           Input: <integer> cipherText
           Output: <integer> plainText
        '''
        self._debug_stream("ciphered",cipher)
        cipher=_Long(self.__wordSize).toArray(cipher,self.__nColumns*\
                                             self.__nRows*self.__wordSize)
        #---- TODO: check the cipher have the size to be deciphered
        self._debug_stream("ciphered array",cipher)
        #---- FIXME: State should be protected in memory 
        #            to avoid side channel attacks
        state=_State(self.__nRows,self.__nColumns,
                    self._logLevel).fromArray(cipher)
        self._debug_stream("state",state)
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),
                                            (self.__nRounds+1)*\
                                            (self.__nColumns)))
        self._debug_stream("state",state,self.__nRounds,
                          "decipher->addRoundKey()\t")
        for r in range(self.__nRounds-1,0,-1):#[Nr-1..1] step -1
            state=self._shiftRows.invert(state)
            self._debug_stream("state",state,r,"decipher->invShiftRows()\t")
            state=self._subBytes.invert(state)
            self._debug_stream("state",state,r,"decipher->invSubBytes()\t")
            state=self._addRoundKey.do(state,
                    self._keyExpander.getSubKey((r*self.__nColumns),
                                                (r+1)*(self.__nColumns)))
            self._debug_stream("state",state,r,"decipher->addRoundKey()\t")
            state=self._mixColumns.invert(state)
            self._debug_stream("state",state,r,"decipher->invMixColumns()\t")
        state=self._shiftRows.invert(state)
        self._debug_stream("state",state,0,"decipher->invShiftRows()\t")
        state=self._subBytes.invert(state)
        self._debug_stream("state",state,0,"decipher->invSubBytes()\t")
        state=self._addRoundKey.do(state,
                                   self._keyExpander.getSubKey(0,
                                                               self.__nColumns))
        self._debug_stream("state",state,0,"decipher->addRoundKey()\t")
        plain=_State(self.__nRows,self.__nColumns,
                    self._logLevel).toArray(state)
        self._debug_stream("deciphered array",plain)
        plain=_Long(self.__wordSize).fromArray(plain,self.__nColumns*\
                                              self.__nRows*self.__wordSize)
        self._debug_stream("deciphered",plain)
        return plain

from optparse import OptionParser

def understandInteger(value):
    try:
        if value.startswith('0x'):
            return int(value,16)
        elif value.startswith('0b'):
            return int(value,2)
        elif value.startswith('0'):#first check hexadecimal and binary
            return int(value,8)
        else:
            return int(value)
    except Exception,e:
        return None

def main():
    #---- TODO: introduce parameters to:
    #           - define parameters to use and use random input and key.
    #           - allow to setup by params the input and/or the key, and
    #           - operations to do: cipher and/or decipher
    parser = OptionParser()
    parser.add_option('',"--log-level",default="info",
                      help="Set log level: error,warning,info,debug,trace")
    parser.add_option('',"--rounds",type="int",default=10,
                                                       help="Number of rounds")
    parser.add_option('',"--rows",type="int",default=4,help="Number of rows")
    parser.add_option('',"--columns",type="int",default=4,
                                                      help="Number of columns")
    parser.add_option('',"--wordsize",type="int",default=8,
                                                   help="Bit size of the word")
    parser.add_option('',"--kolumns",type="int",default=4,
                                           help="Number of columns of the key")
    parser.add_option('',"--key",default="0",
                                          help="Key in numeric representation")
    parser.add_option('',"--plainText",default="0",
                                    help="Plaintext in numeric representation")
    parser.add_option('',"--only-keyexpansion",action="store_true",
                      default=False,
                      help="No [de]cipher operations. Made to test the PRG "\
                      "with the key as seed to generate each round subkeys.")
    parser.add_option('',"--calculate-sbox",default=False,action="store_true",
                      help="Instead of use the given Rijndael tables, do the "\
                      "polynomial calculations.")
    #TODO: add options to only [de]cipher 
    #      (the will be also need a --cipherText)
    (options, args) = parser.parse_args()
    key = understandInteger(options.key)
    if key == None:
        print("\n\tError: It was not possible to understand the input key "\
              "'%s' as a number.\n"%(options.key))
        sys.exit(-1)
    gr = GeneralizedRijndael(key=key,
                             nRounds=options.rounds,
                             nRows=options.rows,
                             nColumns=options.columns,
                             wordSize=options.wordsize,
                             nKeyWords=options.kolumns,
                             sboxCalc=options.calculate_sbox,
                             loglevel=_levelFromMeaning(options.log_level))
    if not options.only_keyexpansion:
        plainText = understandInteger(options.plainText)
        if plainText == None:
            print("\n\tError: It was not possible to understand the input "\
                  "plain text '%s' as a number.\n"%(options.plainText))
            sys.exit(-2)
        cipherText = gr.cipher(plainText)
        if int(plainText) != gr.decipher(cipherText):
            print("Error")
        else:
            print("Ok")
        print("Release: %s"%(version()))

if __name__ == "__main__":
    main()
