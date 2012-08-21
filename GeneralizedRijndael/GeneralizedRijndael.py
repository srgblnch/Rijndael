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

    def debug(self,logtext,data=None,round=None,operation=None):
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

    def cipher(self,plain):
        '''plain (1d array) is copied to state matrix. 
           After the inicial round addition, the state is transformed by the 
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
        '''
        self.debug("plain",plain)
        plain = self.__long2array(plain, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the plain have the size to be ciphered
        self.debug("plain array",plain)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = self._makeStateArray(plain)
        self.debug("state",state)
        self._addRoundKey(state,self.__key[0:self.__nColumns])#w[0,Nb-1]
        self.debug("state",state, 0, "cipher->addRoundKey()\t")
        for r in range(1,self.__nRounds):#[1..Nr-1] step 1
            self._subBytes(state)
            self.debug("state",state,r,"cipher->subBytes()\t")
            state = self._shiftRows(state)
            self.debug("state",state,r,"cipher->shiftRows()\t")
            state = self._mixColumns(state)
            self.debug("state",state,r,"cipher->mixColumns()\t")
            self._addRoundKey(state,self.__key[(r*self.__nColumns):(r+1)*(self.__nColumns)])
            self.debug("state",state,r,"cipher->addRoundKey()\t")
        self._subBytes(state)
        self.debug("state",state,self.__nRounds,"cipher->subBytes()\t")
        state = self._shiftRows(state)
        self.debug("state",state,self.__nRounds,"cipher->shiftRows()\t")
        self._addRoundKey(state,self.__key[(self.__nRounds*self.__nColumns):(self.__nRounds+1)*(self.__nColumns)])
        self.debug("state",state,self.__nRounds,"cipher->addRoundKey()\t")
        cipher = self._unmakeStateArray(state)
        self.debug("cipher array",cipher)
        cipher = self.__array2long(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        self.debug("cipher",cipher)
        return cipher#self._unmakeStateArray(state)

    def decipher(self,cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
        '''
        self.debug("cipher",cipher)
        cipher = self.__long2array(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the cipher have the size to be deciphered
        self.debug("cipher array",cipher)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = self._makeStateArray(cipher)
        self.debug("state",state)
        self._addRoundKey(state,self.__key[(self.__nRounds*self.__nColumns):(self.__nRounds+1)*(self.__nColumns)])
        self.debug("state",state,self.__nRounds,"decipher->addRoundKey()\t")
        for r in range(self.__nRounds-1,0,-1):#[Nr-1..1] step -1
            state = self._invertShiftRows(state)
            self.debug("state",state,r,"decipher->invShiftRows()\t")
            self._invertSubBytes(state)
            self.debug("state",state,r,"decipher->invSubBytes()\t")
            self._addRoundKey(state,self.__key[(r*self.__nColumns):(r+1)*(self.__nColumns)])
            self.debug("state",state,r,"decipher->addRoundKey()\t")
            state = self._invertMixColumns(state)
            self.debug("state",state,r,"decipher->invMixColumns()\t")
        state = self._invertShiftRows(state)
        self.debug("state",state,0,"decipher->invShiftRows()\t")
        self._invertSubBytes(state)
        self.debug("state",state,0,"decipher->invSubBytes()\t")
        self._addRoundKey(state,self.__key[0:self.__nColumns])
        self.debug("state",state,0,"decipher->addRoundKey()\t")
        self._unmakeStateArray(state), self.__nColumns*self.__nRows*self.__wordSize
        plain = self._unmakeStateArray(state)
        self.debug("plain array",plain)
        plain = self.__array2long(plain, self.__nColumns*self.__nRows*self.__wordSize)
        self.debug("plain",plain)
        return plain#self._unmakeStateArray(state)

    ####
    # First descent level
    ####
    def _keyExpansion(self,key):
        '''TODO: Document it
        '''
        self.debug("key",key,operation="keyExpansion()\t")
        key = self.__long2array(key, self.__nKeyWords*self.__nRows*self.__wordSize)
        word = [None]*self.__nKeyWords
        self.debug("key array",key,operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            word[i] = self.__wordList2word(key[(self.__nRows*i):(self.__nRows*i)+self.__nRows])
        i = self.__nKeyWords
        while (i < (self.__nColumns*(self.__nRounds+1))):
            self.debug("i", i, operation='keyExpansion()\t')
            temp = word[i-1]
            self.debug("temp", temp, operation='keyExpansion()\t')
            if (i%self.__nKeyWords == 0):
                rotWord = self.__rotWord(temp)
                self.debug("rotWord", rotWord, operation='keyExpansion()\t')
                subWord = self.__subWord(rotWord)
                self.debug("subWord", subWord, operation='keyExpansion()\t')
                Rcon = self.__wordList2word([RC[i/self.__nKeyWords],0,0,0])
                subWord ^= Rcon
                self.debug("Rcon", Rcon, operation='keyExpansion()\t')
                self.debug("subWord with Rcon", subWord, operation='keyExpansion()\t')
            elif i%self.__nKeyWords == 4:
                subWord = self.__subWord(subWord)
                self.debug("subWord", subWord, operation='keyExpansion()\t')
            else:
                subWord = temp
            self.debug("w[i-Nk]", word[i-self.__nKeyWords], operation='keyExpansion()\t')
            word.append(word[i-self.__nKeyWords]^subWord)
            self.debug("w[i]", word[i], operation='keyExpansion()\t')
            i += 1
        self.debug("keyExpanded",word,operation="keyExpansion()\t")
        self.debug("size of key expanded %d"%len(word))
        return word

    def __long2array(self,input,length):
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
        o = 0
        for i in range(length/self.__wordSize):
            o |= (input[i]<<(((length/self.__wordSize)-i-1)*self.__wordSize))
        return o

    def _makeStateArray(self,input):
        '''Give one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
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
            self.debug("state[%d]"%i, state[i])
        self.debug("makeArray",state)
        return state

    def _unmakeStateArray(self,state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
        '''
        output = []
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        self.debug("unmakeArray",output)
        return output

    def _addRoundKey(self,state,subkey):
        '''The round key is XORted to the state elements.
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
        '''process the state matrix using a non-linear substitution table (sbox)
           operates each byte independently.
        '''
        self.__sboxTransformation(state,self._sbox)

    def _invertSubBytes(self,state):
        '''Inverse of the subBytes() method.
        '''
        self.__sboxTransformation(state,self._sbox_inverted)

    def _shiftRows(self,state):
        '''cyclical left shift of the row 'i' of the state matrix by 'i' positions
           s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
        '''
        newState = []
        for i in range(self.__nRows):
            newState.append(self.__shift(state[i], i))
        return newState

    def _invertShiftRows(self,state):
        '''Inverse of the shiftRows() method.
        '''
        newState = []
        for i in range(self.__nRows):
            newState.append(self.__shift(state[i], -i))
        return newState

    def _mixColumns(self,state):
        '''Transformation to mix the data of the columns (independently 
           between them) of the state matrix.
        '''
        return self.__matrixPolynomialModularProduct(self._cx, state)
    def _invertMixColumns(self,state):
        '''Inverse of the mixColumns() method.
        '''
        return self.__matrixPolynomialModularProduct(self._dx, state)

    #### 
    # Second descent level
    ####
    def __rotWord(self,w):
        '''Used in the key expansion for a cyclic permutation of a word.
        '''
        #Parentesis are very important
        wordMask = int('0b'+('1'*self.__wordSize)+('0'*(self.__wordSize*(self.__nColumns-1))),2)
        shiftMask = int('0b'+('1'*(self.__wordSize*(self.__nColumns))),2)
        return (((w & wordMask) >> (self.__wordSize*(self.__nRows-1))) | ((w << self.__wordSize)&shiftMask))

    def __subWord(self,word):
        '''Used in the key expansion to apply the sbox to a word.
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
        '''
        newState = deepcopy(state)
        for c in range(self.__nColumns):
            shifted_cx = self.__shift(cx, self.__nRows-1)
            for r in range(self.__nRows):
                #self.debug("  a(x)  ",shifted_cx)
                #self.debug("  s[%d]  "%(r), [state[rbis][c] for rbis in range(self.__nRows)])
                newState[r][c] = 0
                for rbis in range(self.__nRows):
                    newState[r][c] ^= self.__productGF(shifted_cx[rbis], state[rbis][c])
                #self.debug("s'[%d][%d]"%(r,c), newState[r][c])
                shifted_cx = self.__shift(shifted_cx, -1)
        return newState

    #### 
    # Third descent level
    ####
    def __productGF(self,a,b):
        '''multiplication of polynomials modulo an irreductible pylinomial of 
           field's degree. Over F_{2^8} this polynomial is 
           m(x) = x^8+x^4+x^3+x+1
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
        a <<= 1
        if a & (1<<binlen(m)-1): a ^= m
        return a

    def __hexValue2MatrixCoords(self,value):
        if self.__wordSize%2 == 1:
            raise Exception("(__hexValue2MatrixCoords)",
                            "Matrix coordinates impossible for an odd %d wordsize"\
                            %(self.__wordSize))
        cmask = '0b'+'1'*(self.__wordSize/2)
        rmask = '0b'+'1'*(self.__wordSize/2)+'0'*(self.__wordSize/2)
        c = (value & int(cmask,2))
        r = (value & int(rmask,2))>>(self.__wordSize/2)
        return r,c

    def __wordList2word(self,wordList):
        word = 0
        for j in range(self.__nRows):
            word += wordList[j]<< self.__wordSize*(self.__nRows-j-1)
        return word

    def __word2wordList(self,word):
        wordArray = []
        mask = int('0b'+'1'*self.__wordSize,2)
        for i in range(self.__nRows):
            wordArray.append((word>>self.__wordSize*i)&mask)
        return wordArray

    def unitTestCompare(self,calculation,expected):
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
        srv.debug("should be", plainText)

def aes128(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=10,nRows=4,nColumns=4,wordSize=8,nKeyWords=4,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("should be", plainText)

def aes192(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f1011121314151617
    srv = GeneralizedRijndael(cipherKey,nRounds=12,nKeyWords=6,
                      debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("should be", plainText)

def aes256(debug=False):
    plainText = 0x00112233445566778899aabbccddeeff
    cipherKey = 0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
    srv = GeneralizedRijndael(cipherKey,
                               nRounds=14,nRows=4,nColumns=4,wordSize=8,nKeyWords=8,
                               debug=debug)
    
    cipherText = srv.cipher(plainText)
    resultText = srv.decipher(cipherText)
    
    unitTest = srv.unitTestCompare(plainText,resultText)
    print("Unit Test= %s"%unitTest)
    if not unitTest:
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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
        srv.debug("should be", plainText)

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

def rijndaelAny(rounds,rows,columns,wordSize,kColumns=0,debug=False):
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
    nbits = columns*rows*wordSize
    plain = randint(0,int('0b'+'1'*(nbits),2))
    cipher = rijndael.cipher(plain)
    plainbis = rijndael.decipher(cipher)
    print("(%dx%d) (w=%d,nbits=%d): %s ?= %s"
          %(rows,columns,wordSize,nbits,hex(plain),hex(plainbis)))
    if plain == plainbis: print "Test OK"
    else: print "Agh!"

def rijndael_allowedBlocks():
    from random import randint
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

def keyExpansionTest(rounds,rows,columns,wordSize,kColumns=0,debug=False):
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

unitTestList = [unitTest,cipherExample]
aesList = [aes128,aes192,aes256]
rijndael32List = [rijndael32_32key_228,rijndael32_32key_442,
                  rijndael32_48key_228,rijndael32_48key_442,
                  rijndael32_64key_442,rijndael32_64key_442,
                  rijndael32_128key_228,rijndael32_128key_442]
testsList = unitTestList+aesList+rijndael32List

def main(arg0,arg1,arg2=False):
    if arg1 == "--help":
        print("\nBasic Usage: %s --test=unitTest|cipher-sample|aes[128,192,256] [--debug]\n"%arg0)
        print("Special test modes:\n\trijndael32[:32|48|64|128] Means block size followed the key size")
        print("\tsizes")
        print("\tspecific:rounds,rows,columns,wordsize[,kColumns]")
        print("\tkeyExpansion:rounds,rows,columns,wordsize[,kColumns]\n")
    if arg1.startswith("--test="):
        if arg1.endswith("all"):
            for func in testsList:
                func(arg2)
        elif arg1.endswith("unitTest"):
            for func in unitTestList:
                func(arg2)
        elif arg1.endswith("cipher-sample"):
            cipherExample(arg2)
        elif arg1.endswith("aes"):
            for func in aesList:
                func(arg2)
        elif arg1.endswith("aes128"):
            aes128(arg2)
        elif arg1.endswith("aes192"):
            aes192(arg2)
        elif arg1.endswith("aes256"):
            aes256(arg2)
        elif arg1.endswith("rijndael32"):
            for func in rijndael32List:
                func(arg2)
        elif arg1.endswith("rijndael32.32"):
            rijndael32_32key_228(arg2)
            rijndael32_32key_442(arg2)
        elif arg1.endswith("rijndael32.48"):
            rijndael32_48key_228(arg2)
            rijndael32_48key_442(arg2)
        elif arg1.endswith("rijndael32.64"):
            rijndael32_64key_228(arg2)
            rijndael32_64key_442(arg2)
        elif arg1.endswith("rijndael32.128"):
            rijndael32_128key_228(arg2)
            rijndael32_128key_442(arg2)
        elif arg1.count("loop"):
            bar = arg1.split('_')[1]
            foo = int(bar)
            rijndael32_128key_loop(foo)
        elif arg1.count("sizes"):
            rijndael_allowedBlocks()
        elif arg1.count("specific"):
            arg1 = arg1.split("specific:")[1].split(",")
            if len(arg1) == 4:
                rounds,rows,columns,wordSize = arg1
                rijndaelAny(int(rounds),int(rows),int(columns),int(wordSize),arg2)
            elif len(arg1) == 5:
                rounds,rows,columns,wordSize,kColumns = arg1
                rijndaelAny(int(rounds),int(rows),int(columns),int(wordSize),int(kColumns),arg2)
            else:
                print("Unrecognized specification for the test. Try \"--help\".")
        elif arg1.count("keyExpansion"):
            arg1 = arg1.split("keyExpansion:")[1].split(",")
            if len(arg1) == 4:
                rounds,rows,columns,wordSize = arg1
                keyExpansionTest(int(rounds),int(rows),int(columns),int(wordSize),int(columns),arg2)
            elif len(arg1) == 5:
                rounds,rows,columns,wordSize,kColumns = arg1
                keyExpansionTest(int(rounds),int(rows),int(columns),int(wordSize),int(kColumns),arg2)
            else:
                print("Unrecognized specification for the test. Try \"--help\".")
        else:
            print("Unrecognized option. Try \"--help\".")

if __name__ == "__main__":
    arg0 = sys.argv[0]
    if len(sys.argv) < 2:
        arg1 = "--help"
    else:
        arg1 = sys.argv[1]
    if len(sys.argv) == 3 and sys.argv[2] == "--debug":
        print("Debug mode")
        arg2 = True
    else:
        arg2 = False
    try:
        main(arg0,arg1,arg2)
    except Exception,e:
        print("\nException for option %s, with reason %s\n"%(arg1,e))
        if arg2:
            traceback.print_exc()
