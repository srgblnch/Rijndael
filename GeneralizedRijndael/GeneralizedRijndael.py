#!/usr/bin/env python

##############################################################################
##
## file: GeneralizedRijndael.py
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

####
# This variant class for the Rijndael symmetric cryptosystem is made to extend
# its possibilities above and below the AES standard block size. Allowing to
# make the matrix bigger or smaller and at the same time be able to change
# the word size the data blocks can be adapted to the user needs.
# Apart of that the key size can also be tuned in some range of the data block.
#
# nRows * nColumns * wordSize = rijndael size
#   4   *    4     *    8     = 128 => AES {128,192,256} key sizes
#   2   *    2     *    8     =  32 => rijndael variant {32,48,64} key sizes
#   4   *    4     *    2     =  32 => another rijndael variant
# and so on.
####

import sys
import traceback

from copy import deepcopy

from sboxes import *
binlen = lambda x: len(bin(x))-2

#TODO: understand who this RC is generated
# RC[1] = 0x01
# RC[i] = x * RC[i-1] = x**(i-1)
RC = [
0x8D,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36,0x6C,0xD8,0xAB,0x4D,0x9A,
0x2F,0x5E,0xBC,0x63,0xC6,0x97,0x35,0x6A,0xD4,0xB3,0x7D,0xFA,0xEF,0xC5,0x91,0x39,
0x72,0xE4,0xD3,0xBD,0x61,0xC2,0x9F,0x25,0x4A,0x94,0x33,0x66,0xCC,0x83,0x1D,0x3A,
0x74,0xE8,0xCB,0x8D,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36,0x6C,0xD8,
0xAB,0x4D,0x9A,0x2F,0x5E,0xBC,0x63,0xC6,0x97,0x35,0x6A,0xD4,0xB3,0x7D,0xFA,0xEF,
0xC5,0x91,0x39,0x72,0xE4,0xD3,0xBD,0x61,0xC2,0x9F,0x25,0x4A,0x94,0x33,0x66,0xCC ,
0x83,0x1D,0x3A,0x74,0xE8,0xCB,0x8D,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,
0x36,0x6C,0xD8,0xAB,0x4D,0x9A,0x2F,0x5E,0xBC,0x63,0xC6,0x97,0x35,0x6A,0xD4,0xB3,
0x7D,0xFA,0xEF,0xC5,0x91,0x39,0x72,0xE4,0xD3,0xBD,0x61,0xC2,0x9F,0x25,0x4A,0x94,
0x33,0x66,0xCC,0x83,0x1D,0x3A,0x74,0xE8,0xCB,0x8D,0x01,0x02,0x04,0x08,0x10,0x20,
0x40,0x80,0x1B,0x36,0x6C,0xD8,0xAB,0x4D,0x9A,0x2F,0x5E,0xBC,0x63,0xC6,0x97,0x35,
0x6A,0xD4,0xB3,0x7D,0xFA,0xEF,0xC5,0x91,0x39,0x72,0xE4,0xD3,0xBD,0x61,0xC2,0x9F,
0x25,0x4A,0x94,0x33,0x66,0xCC,0x83,0x1D,0x3A,0x74,0xE8,0xCB,0x8D,0x01,0x02,0x04,
0x08,0x10,0x20,0x40,0x80,0x1B,0x36,0x6C,0xD8,0xAB,0x4D,0x9A,0x2F,0x5E,0xBC,0x63,
0xC6,0x97,0x35,0x6A,0xD4,0xB3,0x7D,0xFA,0xEF,0xC5,0x91,0x39,0x72,0xE4,0xD3,0xBD,
0x61,0xC2,0x9F,0x25,0x4A,0x94,0x33,0x66,0xCC,0x83,0x1D,0x3A,0x74,0xE8,0xCB
]
#This is to have the Rcon in the key Expansion where Rcon[i] = (RC[i],00,00,00)

class GeneralizedRijndael:
    def __init__(self,key,
                      debug=False,
                      nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                      nKeyWords=4):
        self.__debug = debug
        self.__nRounds = nRounds     #Number of encryption rounds {10,12,14}
        self.__nRows = nRows         #Number of rows in the rectangular arrangement
        self.__nColumns = nColumns   #Number of columns in the rectangular arrangement
        self.__wordSize = wordSize   #in bits, AES is 8 bits word, but here test {2,8}
        self.__nKeyWords = nKeyWords #Usually {4,6,8}
        print("Rijndael(%d,%d,%d,%d): block=%dbits key=%dbits"
              %(self.__nRounds,self.__nRows,self.__nColumns,self.__wordSize,
                self.__nColumns*self.__nRows*self.__wordSize,
                self.__nKeyWords*self.__nRows*self.__wordSize))
        #prepare substructures
        if  self.__wordSize == 8:
            self._sbox = sbox_word8b
            self._sbox_inverted = sbox_word8b_inverted
            self._m = 0b100011011
            if self.__nRows == 4:
                self._cx = [0x3,0x1,0x1,0x2]#MDS matrices (Maximum Distance Separable)
                self._dx = [0xB,0xD,0x9,0xE]#c(x) \otimes d(x) = 1
            elif self.__nRows == 3:
                self._cx = [0xD,0x1,0x1] #FIXME: unknown
                self._dx = [0x3C,0xAA,0x3C]#FIXME: unknown
            elif self.__nRows == 2:
                self._cx = [0x2,0x3]#FIXME: unknown
                self._dx = [0x2,0x3]#FIXME: unknown
        elif  self.__wordSize == 4:
            self._sbox = sbox_word4b
            self._sbox_inverted = sbox_word4b_inverted
            self._m = 0b10000
            if self.__nRows == 4:
                self._cx = self._dx = [0,0,0,0] #FIXME: unknown
            elif self.__nRows == 3:
                self._cx = self._dx = [0,0,0] #FIXME: unknown
            elif self.__nRows == 2:
                self._cx = self._dx = [0,0] #FIXME: unknown
        elif  self.__wordSize == 2:
            self._sbox = sbox_word2b
            self._sbox_inverted = sbox_word2b_inverted
            self._m = 0b100
            if self.__nRows == 4:
                self._cx = self._dx = [0x3,0x1,0x1,0x2]#FIXME: unknown
            elif self.__nRows == 3:
                self._cx = self._dx = [0,0,0] #FIXME: unknown
            elif self.__nRows == 2:
                self._cx = self._dx = [0x2,0x3]#FIXME: unknown
        if not (hasattr(self,"_sbox") or hasattr(self,"_sbox_inverted") or\
                hasattr(self,'_m') or\
                hasattr(self,"_cx") or hasattr(self,"_dx")):
            raise Exception("(__init__)","There is no Sbox for %d wordsize"\
                            %(self.__wordSize))
        #Prepare the key
        self.__key = self._keyExpansion(key)

    def __debug_stream(self,logtext,data=None,round=None,operation=None):
        if self.__debug:
            msg = ""
            if not round == None:
                msg += "Round[%d];"%round
            if not operation == None:
                msg += "%s:"%operation
            msg += logtext
            if not data == None:
                if type(data) in [int,long]:
                    msg += "=%s"%hex(data)
                elif type(data) == list:
                    msg += "=["
                    for element in data:
                        if type(element) in [int,long]:
                            msg += "%4s,"%hex(element)
                        elif type(element) == list:
                            msg += "["
                            for subelement in element:
                                msg += "%4s,"%hex(subelement)
                            msg = msg[:len(msg)-1]+"],"
                        else:
                            msg += "%s,"%element
                    msg = msg[:len(msg)-1]+"]"
                else:
                    msg += "=%s"%(data)
            print msg

    #----# interface methods
    def cipher(self,plain):
        '''plain (1d array) is copied to state matrix. 
           After the inicial round addition, the state is transformed by the 
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        self.__debug_stream("plain",plain)
        plain = self.__long2array(plain, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the plain have the size to be ciphered
        self.__debug_stream("plain array",plain)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = self.__makeStateArray(plain)
        self.__debug_stream("state",state)
        self._addRoundKey(state,self.__key[0:self.__nColumns])#w[0,Nb-1]
        self.__debug_stream("state",state, 0, "cipher->addRoundKey()\t")
        for r in range(1,self.__nRounds):#[1..Nr-1] step 1
            self._subBytes(state)
            self.__debug_stream("state",state,r,"cipher->subBytes()\t")
            state = self._shiftRows(state)
            self.__debug_stream("state",state,r,"cipher->shiftRows()\t")
            state = self._mixColumns(state)
            self.__debug_stream("state",state,r,"cipher->mixColumns()\t")
            self._addRoundKey(state,self.__key[(r*self.__nColumns):(r+1)*(self.__nColumns)])
            self.__debug_stream("state",state,r,"cipher->addRoundKey()\t")
        self._subBytes(state)
        self.__debug_stream("state",state,self.__nRounds,"cipher->subBytes()\t")
        state = self._shiftRows(state)
        self.__debug_stream("state",state,self.__nRounds,"cipher->shiftRows()\t")
        self._addRoundKey(state,self.__key[(self.__nRounds*self.__nColumns):(self.__nRounds+1)*(self.__nColumns)])
        self.__debug_stream("state",state,self.__nRounds,"cipher->addRoundKey()\t")
        cipher = self.__unmakeStateArray(state)
        self.__debug_stream("cipher array",cipher)
        cipher = self.__array2long(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        self.__debug_stream("cipher",cipher)
        return cipher#self.__unmakeStateArray(state)

    def decipher(self,cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        self.__debug_stream("cipher",cipher)
        cipher = self.__long2array(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the cipher have the size to be deciphered
        self.__debug_stream("cipher array",cipher)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = self.__makeStateArray(cipher)
        self.__debug_stream("state",state)
        self._addRoundKey(state,self.__key[(self.__nRounds*self.__nColumns):(self.__nRounds+1)*(self.__nColumns)])
        self.__debug_stream("state",state,self.__nRounds,"decipher->addRoundKey()\t")
        for r in range(self.__nRounds-1,0,-1):#[Nr-1..1] step -1
            state = self._invertShiftRows(state)
            self.__debug_stream("state",state,r,"decipher->invShiftRows()\t")
            self._invertSubBytes(state)
            self.__debug_stream("state",state,r,"decipher->invSubBytes()\t")
            self._addRoundKey(state,self.__key[(r*self.__nColumns):(r+1)*(self.__nColumns)])
            self.__debug_stream("state",state,r,"decipher->addRoundKey()\t")
            state = self._invertMixColumns(state)
            self.__debug_stream("state",state,r,"decipher->invMixColumns()\t")
        state = self._invertShiftRows(state)
        self.__debug_stream("state",state,0,"decipher->invShiftRows()\t")
        self._invertSubBytes(state)
        self.__debug_stream("state",state,0,"decipher->invSubBytes()\t")
        self._addRoundKey(state,self.__key[0:self.__nColumns])
        self.__debug_stream("state",state,0,"decipher->addRoundKey()\t")
        self.__unmakeStateArray(state), self.__nColumns*self.__nRows*self.__wordSize
        plain = self.__unmakeStateArray(state)
        self.__debug_stream("plain array",plain)
        plain = self.__array2long(plain, self.__nColumns*self.__nRows*self.__wordSize)
        self.__debug_stream("plain",plain)
        return plain#self.__unmakeStateArray(state)
    #---- End interface methods

    #----# First descent level
    def _keyExpansion(self,key):
        '''a Pseudo Random Generator that takes the key as a seed to expand 
           it to generate all the subkeys need for each round of the Rijndael.
           Input: <integer> seed
           Output: <integer array> subkeys
           descent methods: ['__rotWord','__subWord']
           auxiliar methods: ['__debug_stream','__long2array','__wordList2word']
        '''
        self.__debug_stream("key",key,operation="keyExpansion()\t")
        key = self.__long2array(key, self.__nKeyWords*self.__nRows*self.__wordSize)
        word = [None]*self.__nKeyWords
        self.__debug_stream("key array",key,operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            word[i] = self.__wordList2word(key[(self.__nRows*i):(self.__nRows*i)+self.__nRows])
        i = self.__nKeyWords
        while (i < (self.__nColumns*(self.__nRounds+1))):
            self.__debug_stream("i", i, operation='keyExpansion()\t')
            temp = word[i-1]
            self.__debug_stream("temp", temp, operation='keyExpansion()\t')
            if (i%self.__nKeyWords == 0):
                rotWord = self.__rotWord(temp)
                self.__debug_stream("rotWord", rotWord, operation='keyExpansion()\t')
                subWord = self.__subWord(rotWord)
                self.__debug_stream("subWord", subWord, operation='keyExpansion()\t')
                Rcon = self.__wordList2word([RC[i/self.__nKeyWords],0,0,0])
                subWord ^= Rcon
                self.__debug_stream("Rcon", Rcon, operation='keyExpansion()\t')
                self.__debug_stream("subWord with Rcon", subWord, operation='keyExpansion()\t')
            elif i%self.__nKeyWords == 4:
                subWord = self.__subWord(subWord)
                self.__debug_stream("subWord", subWord, operation='keyExpansion()\t')
            else:
                subWord = temp
            self.__debug_stream("w[i-Nk]", word[i-self.__nKeyWords], operation='keyExpansion()\t')
            word.append(word[i-self.__nKeyWords]^subWord)
            self.__debug_stream("w[i]", word[i], operation='keyExpansion()\t')
            i += 1
        self.__debug_stream("keyExpanded",word,operation="keyExpansion()\t")
        self.__debug_stream("size of key expanded %d"%len(word))
        return word

    #----## round transformation methods.
    def _addRoundKey(self,state,subkey):
        '''One of the round transformation methods.
           The round key (from the PRG) list of arrays (can be thougth as a 
           matrix), is bitwise XORted with the state matrix.
           Input: <integer arrays> state, subkey
           Output: <integer arrays> state (modified)
           descent methods: []
           auxiliar methods: ['__word2wordList']
        '''
#        for i in range(self.__nRows):
#            for j in range(self.__nColumns):
#                state[i][j] ^= subkey[j]#FIXME: check this index are correct
#
        for j in range(self.__nColumns):
            byteSubkey = self.__word2wordList(subkey[j])
            byteSubkey.reverse()
            for i in range(self.__nRows):
                state[i][j] ^= byteSubkey[i]
    
    def _subBytes(self,state):
        '''One of the round transformation methods.
           process the state matrix using a non-linear substitution table 
           (sbox) operates each byte independently.
           The sbox transformation is a faster way to compose two 
           transformations (multiplicative inverse and an affine transformation,
           both over a polynomial field F_{2^w}) to save calculations.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: ['__sboxTransformation']
           auxiliar methods: []
        '''
        self.__sboxTransformation(state,self._sbox)

    def _invertSubBytes(self,state):
        '''Inverse of the subBytes() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: ['__sboxTransformation']
           auxiliar methods: []
        '''
        self.__sboxTransformation(state,self._sbox_inverted)

    def _shiftRows(self,state):
        '''One of the round transformation methods.
           cyclical left shift of the row 'i' of the state matrix by 'i' positions
           s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: []
           auxiliar methods: []
        '''
        newState = []
        for i in range(self.__nRows):
            newState.append(self.__shift(state[i], i))
        return newState

    def _invertShiftRows(self,state):
        '''Inverse of the shiftRows() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: []
           auxiliar methods: []
        '''
        newState = []
        for i in range(self.__nRows):
            newState.append(self.__shift(state[i], -i))
        return newState

    def _mixColumns(self,state):
        '''One of the round transformation methods.
           Transformation to mix the data of the columns (independently 
           between them) of the state matrix.
           Consider the columns of the state as polynomials rings, being each
           cell as a coefficient, that is nested a polynomial field F_{2^w}.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: ['__matrixPolynomialModularProduct']
           auxiliar methods: []
        '''
        return self.__matrixPolynomialModularProduct(self._cx, state)
    def _invertMixColumns(self,state):
        '''Inverse of the mixColumns() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
           descent methods: ['__matrixPolynomialModularProduct']
           auxiliar methods: []
        '''
        return self.__matrixPolynomialModularProduct(self._dx, state)
    #---- End round transformation methods.
    #---- End First descent level

    #----# Second descent level
    def __rotWord(self,w):
        '''Used in the key expansion for a cyclic permutation of a word.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        #Parentesis are very important
        wordMask = int('0b'+('1'*self.__wordSize)+('0'*(self.__wordSize*(self.__nColumns-1))),2)
        shiftMask = int('0b'+('1'*(self.__wordSize*(self.__nColumns))),2)
        return (((w & wordMask) >> (self.__wordSize*(self.__nRows-1))) | ((w << self.__wordSize)&shiftMask))

    def __subWord(self,word):
        '''Used in the key expansion to apply the sbox to a word.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        wordArray = self.__word2wordList(word)
        self.__sboxTransformation(wordArray, self._sbox)
        wordArray.reverse()#FIXME: Where is this in the fips pub-197?
        return self.__wordList2word(wordArray)

    def __sboxTransformation(self,state,sbox):
        '''Given the content of one cell of the state matrix, 'divide' in 2 halfs.
           The upper is understood as the row and the lower as the column in the sbox.
           The sbox is a paramenter because the transformation use one sbox or
           its invers, but the procedure is the same.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        for i in range(len(state)):
            if type(state[i]) == list:
                for j in range(len(state[i])):
                    r,c = self.__hexValue2MatrixCoords(state[i][j])
                    state[i][j] = sbox[r][c]
            else:
                r,c = self.__hexValue2MatrixCoords(state[i])
                state[i] = sbox[r][c]

    def __shift(self,l,n):
        '''cyclic rotation of the list 'l' y 'n' elements. 
           Positive n's means left, negative n's means right.
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        return l[n:] + l[:n]

    def __matrixPolynomialModularProduct(self,cx,state):
        '''Given two polynomials over F_{2^8} multiplie them modulo x^{4}+1
           s'(x) = a(x) \otimes s(x)
           [s'_0,c]   [a_3 a_0 a_1 a_2] [s_0,c]
           [s'_1,c] = [a_2 a_3 a_0 a_1] [s_1,c]
           [s'_2,c]   [a_1 a_2 a_3 a_0] [s_2,c]
           [s'_3,c]   [a_0 a_1 a_2 a_3] [s_3,c]
           s'_0,c = (a_3 \bullet s_0,c) \oplus (a_0 \bullet s_1,c) \oplus
                    (a_1 \bullet s_2,c) \oplus (a_2 \bullet s_3,c)
           s'_1,c = (a_2 \bullet s_0,c) \oplus (a_3 \bullet s_1,c) \oplus
                    (a_0 \bullet s_2,c) \oplus (a_1 \bullet s_3,c)
           s'_2,c = (a_1 \bullet s_0,c) \oplus (a_2 \bullet s_1,c) \oplus
                    (a_3 \bullet s_2,c) \oplus (a_0 \bullet s_3,c)
           s'_3,c = (a_0 \bullet s_0,c) \oplus (a_1 \bullet s_1,c) \oplus
                    (a_2 \bullet s_2,c) \oplus (a_3 \bullet s_3,c)
           Where \bullet is the finite field (F_{2^8}) multiplication,
           and \oplus an xor operation
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        newState = deepcopy(state)
        for c in range(self.__nColumns):
            shifted_cx = self.__shift(cx, self.__nRows-1)
            for r in range(self.__nRows):
                #self.__debug_stream("  a(x)  ",shifted_cx)
                #self.__debug_stream("  s[%d]  "%(r), [state[rbis][c] for rbis in range(self.__nRows)])
                newState[r][c] = 0
                for rbis in range(self.__nRows):
                    newState[r][c] ^= self.__productGF(shifted_cx[rbis], state[rbis][c])
                #self.__debug_stream("s'[%d][%d]"%(r,c), newState[r][c])
                shifted_cx = self.__shift(shifted_cx, -1)
        return newState
    #---- End Second descent level

    #----# Third descent level
    #----## Mathematic methods
    def __productGF(self,a,b):
        '''multiplication of polynomials modulo an irreductible pylinomial of 
           field's degree. Over F_{2^8} this polynomial is 
           m(x) = x^8+x^4+x^3+x+1
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        #FIXME: made sure about the irreductible polynomials used
        b_ = b
        xor = []
        a_i = [a]
        for i in range(binlen(b)):
            if b_&1:
                xor.append(a_i[len(a_i)-1])
            b_ >>= 1
            a_i.append(self.__xtime(a_i[len(a_i)-1], self._m))
        r = 0
        for x in xor:
            r ^= x
        return r

    def __xtime(self,a,m=0x11b):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        a <<= 1
        if a & (1<<binlen(m)-1): a ^= m
        return a
    #---- End Mathematic methods

    #----## bit methods
    def __hexValue2MatrixCoords(self,value):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        if self.__wordSize%2 == 1:
            raise Exception("(__hexValue2MatrixCoords)",
                            "Matrix coordinates impossible for an odd %d wordsize"\
                            %(self.__wordSize))
        cmask = '0b'+'1'*(self.__wordSize/2)
        rmask = '0b'+'1'*(self.__wordSize/2)+'0'*(self.__wordSize/2)
        c = (value & int(cmask,2))
        r = (value & int(rmask,2))>>(self.__wordSize/2)
        return r,c
    #---- End bit methods

    #----## integer manipulation methods
    def __long2array(self,input,length):
        '''Auxilliar method to unpack an integer to a set of smaller integers 
           in an array. The size of each of the integers in the set have the 
           wordSize
           Input: <integer>
           Output: <integer array>
           descent methods: []
           auxiliar methods: []
        '''
        if input>int('0b'+('1'*length),2):
            raise Exception("(long2array)","Too big input for %d lenght"%(length))
        o = []
        #cut the input blocs of the word size
        mask = (int('0b'+('1'*self.__wordSize),2)<<(length-self.__wordSize))
        for i in range(length/self.__wordSize):
            e = (input&mask)>>(((length/self.__wordSize)-i-1)*self.__wordSize)
            o.append(int(e))
            mask >>= self.__wordSize
        return o

    def __array2long(self,input,length):
        '''Auxiliar method to pack an array of integers (with #wordSize bits)
           onto one integer.
           Input: <integer array>
           Output: <integer>
           descent methods: []
           auxiliar methods: []
        '''
        o = 0
        for i in range(length/self.__wordSize):
            o |= (input[i]<<(((length/self.__wordSize)-i-1)*self.__wordSize))
        return o

    def __makeStateArray(self,input):
        '''Given a one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
           Input: <integer array> 1d
           Output: <integer arrays> 2d
           descent methods: []
           auxiliar methods: []
        '''
        #FIXME: what happens if the size of input is not r*c?
        #       if exceeds, the rest are ignored;
        #       if not enough, empty cells
        state = [None]*self.__nRows
        for i in range(len(input)):
            row = i%self.__nRows
            if row == i:
                state[row] = [input[i]]
            else:
                state[row].append(input[i])
        for i in range(self.__nRows):
            self.__debug_stream("state[%d]"%i, state[i])
        self.__debug_stream("makeArray",state)
        return state

    def __unmakeStateArray(self,state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
           Input: <integer arrays> 2d
           Output: <integer array> 1d
           descent methods: []
           auxiliar methods: []
        '''
        output = []
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        self.__debug_stream("unmakeArray",output)
        return output

    def __wordList2word(self,wordList):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        word = 0
        for j in range(self.__nRows):
            word += wordList[j]<< self.__wordSize*(self.__nRows-j-1)
        return word

    def __word2wordList(self,word):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        wordArray = []
        mask = int('0b'+'1'*self.__wordSize,2)
        for i in range(self.__nRows):
            wordArray.append((word>>self.__wordSize*i)&mask)
        return wordArray
    #---- End integer manipulation methods
    #---- End Third descent level

    #----# test methods
    def unitTestCompare(self,calculation,expected):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        if not type(calculation) == type(expected):
            print("Ooh!")
            return False
        if type(calculation) == list:
            for i in range(len(calculation)):
                recursive = self.unitTestCompare(calculation[i], expected[i])
                if recursive == False: return False
            return True
        elif type(calculation) in [int,long]:
            if calculation == expected: return True
            else: return False
    #---- End test methods

# end class GeneralizedRijndael
####
