#!/usr/bin/env python

#---- licence header
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

from copy import deepcopy
from sboxes import *

binlen = lambda x: len(bin(x))-2

debug = True#by default

def debug_stream(logtext,data=None,round=None,operation=None):
    if debug:
        msg = ""
        if not round == None: msg += "Round[%d];"%round
        if not operation == None: msg += "%s:"%operation
        msg += logtext
        if not data == None:
            if type(data) in [int,long]: msg += "=%s"%hex(data)
            elif type(data) == list:
                msg += "=["
                for element in data:
                    if type(element) in [int,long]: msg += "%4s,"%hex(element)
                    elif type(element) == list:
                        msg += "["
                        for subelement in element: msg += "%4s,"%hex(subelement)
                        msg = msg[:len(msg)-1]+"],"
                    else: msg += "%s,"%element
                msg = msg[:len(msg)-1]+"]"
            else: msg += "=%s"%(data)
        print msg

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
        debug = debug
        self.__nRounds = nRounds     #Number of encryption rounds {10,12,14}
        self.__nRows = nRows         #Number of rows in the rectangular arrangement
        self.__nColumns = nColumns   #Number of columns in the rectangular arrangement
        self.__wordSize = wordSize   #in bits, AES is 8 bits word, but here test {2,8}
        self.__nKeyWords = nKeyWords #Usually {4,6,8}
        debug_stream(logtext="Rijndael(%d,%d,%d,%d): block=%dbits key=%dbits"
                     %(self.__nRounds,self.__nRows,self.__nColumns,self.__wordSize,
                       self.__nColumns*self.__nRows*self.__wordSize,
                       self.__nKeyWords*self.__nRows*self.__wordSize))
        self._keyExpander = KeyExpander(key,self.__nRounds,self.__nRows,self.__nColumns,self.__wordSize,self.__nKeyWords)
        self._subBytes = SubBytes(wordSize)
        self._shiftRows = ShiftRows(nRows)
        self._mixColumns = MixColumns(nRows,nColumns,wordSize)
        self._addRoundKey = AddRoundKey(nRows,nColumns,wordSize)
        
    def cipher(self,plain):
        '''plain (1d array) is copied to state matrix. 
           After the inicial round addition, the state is transformed by the 
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
           Input: <integer> plainText
           Output: <integer> cipherText
        '''
        debug_stream("plaintext",plain)
        plain = Long(self.__wordSize).toArray(plain, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the plain have the size to be ciphered
        debug_stream("plaintext array",plain)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = State(self.__nRows,self.__nColumns).fromArray(plain)
        debug_stream("state",state)
        state = self._addRoundKey.do(state,self._keyExpander.getSubKey(0,self.__nColumns))#w[0,Nb-1]
        debug_stream("state",state, 0, "cipher->addRoundKey()\t")
        for r in range(1,self.__nRounds):#[1..Nr-1] step 1
            state = self._subBytes.do(state)
            debug_stream("state",state,r,"cipher->subBytes()\t")
            state = self._shiftRows.do(state)
            debug_stream("state",state,r,"cipher->shiftRows()\t")
            state = self._mixColumns.do(state)
            debug_stream("state",state,r,"cipher->mixColumns()\t")
            state = self._addRoundKey.do(state,self._keyExpander.getSubKey((r*self.__nColumns),(r+1)*(self.__nColumns)))
            debug_stream("state",state,r,"cipher->addRoundKey()\t")
        state = self._subBytes.do(state)
        debug_stream("state",state,self.__nRounds,"cipher->subBytes()\t")
        state = self._shiftRows.do(state)
        debug_stream("state",state,self.__nRounds,"cipher->shiftRows()\t")
        state = self._addRoundKey.do(state,self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),(self.__nRounds+1)*(self.__nColumns)))
        debug_stream("state",state,self.__nRounds,"cipher->addRoundKey()\t")
        cipher = State(self.__nRows,self.__nColumns).toArray(state)
        debug_stream("ciphertext array",cipher)
        cipher = Long(self.__wordSize).fromArray(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        debug_stream("ciphertext",cipher)
        return cipher

    def decipher(self,cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
           Input: <integer> cipherText
           Output: <integer> plainText
        '''
        debug_stream("ciphered",cipher)
        cipher = Long(self.__wordSize).toArray(cipher, self.__nColumns*self.__nRows*self.__wordSize)
        #TODO: check the cipher have the size to be deciphered
        debug_stream("ciphered array",cipher)
        #FIXME: State should be protected in memory to avoid side channel attacks
        state = State(self.__nRows,self.__nColumns).fromArray(cipher)
        debug_stream("state",state)
        state = self._addRoundKey.do(state,self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),(self.__nRounds+1)*(self.__nColumns)))
        debug_stream("state",state,self.__nRounds,"decipher->addRoundKey()\t")
        for r in range(self.__nRounds-1,0,-1):#[Nr-1..1] step -1
            state = self._shiftRows.invert(state)
            debug_stream("state",state,r,"decipher->invShiftRows()\t")
            state = self._subBytes.invert(state)
            debug_stream("state",state,r,"decipher->invSubBytes()\t")
            state = self._addRoundKey.do(state,self._keyExpander.getSubKey((r*self.__nColumns),(r+1)*(self.__nColumns)))
            debug_stream("state",state,r,"decipher->addRoundKey()\t")
            state = self._mixColumns.do(state)
            debug_stream("state",state,r,"decipher->invMixColumns()\t")
        state = self._shiftRows.do(state)
        debug_stream("state",state,0,"decipher->invShiftRows()\t")
        state = self._subBytes.invert(state)
        debug_stream("state",state,0,"decipher->invSubBytes()\t")
        state = self._addRoundKey.do(state,self._keyExpander.getSubKey(0,self.__nColumns))
        debug_stream("state",state,0,"decipher->addRoundKey()\t")
        plain = State(self.__nRows,self.__nColumns).toArray(state)
        debug_stream("deciphered array",plain)
        plain = Long(self.__wordSize).fromArray(plain, self.__nColumns*self.__nRows*self.__wordSize)
        debug_stream("deciphered",plain)
        return plain
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

#----# First descent level
class KeyExpander:
    def __init__(self,key,nRounds,nRows,nColumns,wordSize,nKeyWords):
        '''a Pseudo Random Generator that takes the key as a seed to expand 
           it to generate all the subkeys need for each round of the Rijndael.
           Input: <integer> seed
           Output: <integer array> subkeys
        '''
        self.__key = key
        self.__nRounds = nRounds
        self.__nRows = nRows
        self.__nColumns = nColumns
        self.__wordSize = wordSize
        self.__nKeyWords = nKeyWords
        self.__sbox = SBox(wordSize)
        self.__word = Word(nRows,wordSize)
        self.__keyExpanded = [None]*self.__nKeyWords
        
        debug_stream("key",key,operation="keyExpansion()\t")
        key = Long(self.__wordSize).toArray(key, self.__nKeyWords*self.__nRows*self.__wordSize)
        self.__keyExpanded = [None]*self.__nKeyWords
        debug_stream("key array",key,operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            self.__keyExpanded[i] = Word(self.__nRows,self.__wordSize).fromList(key[(self.__nRows*i):(self.__nRows*i)+self.__nRows])
        i = self.__nKeyWords
        while (i < (self.__nColumns*(self.__nRounds+1))):
            debug_stream("i", i, operation='keyExpansion()\t')
            temp = self.__keyExpanded[i-1]
            debug_stream("temp", temp, operation='keyExpansion()\t')
            if (i%self.__nKeyWords == 0):
                rotWord = self.__rotWord(temp)
                debug_stream("rotWord", rotWord, operation='keyExpansion()\t')
                subWord = self.__subWord(rotWord)
                debug_stream("subWord", subWord, operation='keyExpansion()\t')
                Rcon = Word(self.__nRows,self.__wordSize).fromList([RC[i/self.__nKeyWords],0,0,0])
                subWord ^= Rcon
                debug_stream("Rcon", Rcon, operation='keyExpansion()\t')
                debug_stream("subWord with Rcon", subWord, operation='keyExpansion()\t')
            elif i%self.__nKeyWords == 4:
                subWord = self.__subWord(subWord)
                debug_stream("subWord", subWord, operation='keyExpansion()\t')
            else:
                subWord = temp
            debug_stream("w[i-Nk]", self.__keyExpanded[i-self.__nKeyWords], operation='keyExpansion()\t')
            self.__keyExpanded.append(self.__keyExpanded[i-self.__nKeyWords]^subWord)
            debug_stream("w[i]", self.__keyExpanded[i], operation='keyExpansion()\t')
            i += 1
        debug_stream("keyExpanded",self.__keyExpanded,operation="keyExpansion()\t")
        debug_stream("size of key expanded %d"%len(self.__keyExpanded))

    def getSubKey(self,start,end):
        return self.__keyExpanded[start:end]
    def __rotWord(self,w):
        '''Used in the key expansion. A cyclic shift of the bytes in the word.
           Input: <integer> w (with length wordSize)
           Output: <integer> w (modified)
        '''
        #Parentesis are very important
        wordMask = int('0b'+('1'*self.__wordSize)+('0'*(self.__wordSize*(self.__nColumns-1))),2)
        shiftMask = int('0b'+('1'*(self.__wordSize*(self.__nColumns))),2)
        return (((w & wordMask) >> (self.__wordSize*(self.__nRows-1))) | ((w << self.__wordSize)&shiftMask))

    def __subWord(self,word):
        '''Used in the key expansion. Apply a table lookup (sbox) to the set 
           of words.
           Input: <integer> word
           Output: <integer> word
        '''
        wordArray = self.__word.toList(word)
        self.__sbox.transform(wordArray)
        wordArray.reverse()#FIXME: Where is this in the fips pub-197?
        return self.__word.fromList(wordArray)

class SubBytes:
    def __init__(self,wordSize):
        self.__sbox = SBox(wordSize)
    def do(self,input):
        return self.__sbox.transform(input)
    def invert(self,input):
        return self.__sbox.transform(input,invert=True)#It's the same but different sbox

class ShiftRows:
    def __init__(self,nRows):
        self.__nRows = nRows
    def do(self,input):
        '''One of the round transformation methods.
           cyclical left shift of the row 'i' of the state matrix by 'i' positions
           s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output = []
        for i in range(self.__nRows):
            output.append(shift(input[i], i))
        return output
    def invert(self,input):
        '''Inverse of the shiftRows() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output = []
        for i in range(self.__nRows):
            output.append(shift(input[i], -i))
        return output

class MixColumns:
    def __init__(self,nRows,nColumns,wordSize):
        #FIXME: refactor this horrible if
        if wordSize == 8:
            if nRows == 4:
                self.__cx = [0x3,0x1,0x1,0x2]#MDS matrices (Maximum Distance Separable)
                self.__dx = [0xB,0xD,0x9,0xE]#c(x) \otimes d(x) = 1
            elif nRows == 3:
                self.__cx = [0xD,0x1,0x1] #FIXME: unknown
                self.__dx = [0x3C,0xAA,0x3C]#FIXME: unknown
            elif nRows == 2:
                self.__cx = [0x2,0x3]#FIXME: unknown
                self.__dx = [0x2,0x3]#FIXME: unknown
            polynomialModule = 0b100011011
        elif  wordSize == 4:
            if nRows == 4:
                self.__cx = self.__dx = [0,0,0,0] #FIXME: unknown
            elif nRows == 3:
                self.__cx = self.__dx = [0,0,0] #FIXME: unknown
            elif nRows == 2:
                self.__cx = self.__dx = [0,0] #FIXME: unknown
            polynomialModule = 0b10000
        elif  wordSize == 2:
            if nRows == 4:
                self.__cx = self.__dx = [0x3,0x1,0x1,0x2]#FIXME: unknown
            elif nRows == 3:
                self.__cx = self.__dx = [0,0,0] #FIXME: unknown
            elif nRows == 2:
                self.__cx = self.__dx = [0x2,0x3]#FIXME: unknown
            polynomialModule = 0b100
        self.__polynomialRing = PolynomialRing(nRows,nColumns,polynomialModule)
    def do(self,input):
        return self.__polynomialRing.product(self.__cx, input)
    def invert(self,input):
        return self.__polynomialRing.product(self.__dx, input)

class AddRoundKey:
    def __init__(self,nRows,nColumns,wordSize):
        self.__nRows = nRows
        self.__nColumns = nColumns
        self.__word = Word(nRows,wordSize)
    def do(self,input,subkey):
        '''One of the round transformation methods.
           The round key (from the PRG) list of arrays (can be thougth as a 
           matrix), is bitwise XORted with the state matrix.
           Input: <integer arrays> state, subkey
           Output: <integer arrays> state (modified)
        '''
        output = input
        for j in range(self.__nColumns):
            byteSubkey = self.__word.toList(subkey[j])
            byteSubkey.reverse()
            for i in range(self.__nRows):
                bar = output[i][j]
                bar ^= byteSubkey[i]
                output[i][j] = bar
        return output

#---- End First descent level

#----# Second descent level
class SBox:
    def __init__(self,wordSize):
        #TODO: this must be avel to be modified to use a sbox as a table or as the pure calculations
        self.__wordSize = wordSize
        if wordSize == 8:
            self._sbox = sbox_word8b
            self._sbox_inverted = sbox_word8b_inverted
        elif  self.__wordSize == 4:
            self._sbox = sbox_word4b
            self._sbox_inverted = sbox_word4b_inverted
        elif  self.__wordSize == 2:
            self._sbox = sbox_word2b
            self._sbox_inverted = sbox_word2b_inverted
        if not (hasattr(self,"_sbox") or hasattr(self,"_sbox_inverted")):
            raise Exception("(__init__)","There is no Sbox for %d wordsize"\
                            %(self.__wordSize))
    def transform(self,state,invert=False):
        '''Given the content of one cell of the state matrix, 'divide' in 2 halfs.
           The upper is understood as the row and the lower as the column in the sbox.
           The sbox is a paramenter because the transformation use one sbox or
           its invers, but the procedure is the same.
           Input:
           Output:
        '''
        if invert: sbox = self._sbox_inverted
        else: sbox = self._sbox
        for i in range(len(state)):
            if type(state[i]) == list:
                for j in range(len(state[i])):
                    r,c = self.__hexValue2MatrixCoords(state[i][j])
                    state[i][j] = sbox[r][c]
            else:
                r,c = self.__hexValue2MatrixCoords(state[i])
                state[i] = sbox[r][c]
        return state
    def __hexValue2MatrixCoords(self,value):
        '''Split the input in to equal halfs that will be used as coordinates 
           in the sbox transformations.
           Input: <integer> value
           Output: <integer> row, <integer> column
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

class PolynomialRing:
    def __init__(self,r,c,m=0x11b):
        self.__nRows = r
        self.__nColumns = c
        self.__polynomialsubfield = PolynomialField(m)
    def product(self,ax,sx):
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
        '''
        debug_stream("a(x)", ax, operation='PolynomialRing.product()\t')
        debug_stream("s(x)", sx, operation='PolynomialRing.product()\t')
        res = deepcopy(sx)#[[0]*self.__nRows]*self.__nColumns#FIXME: was 'deepcopy(sx)' but is correct the
        debug_stream("s'(x)", res, operation='PolynomialRing.product()\t')
        for c in range(self.__nColumns):
            shifted_ax = shift(ax, self.__nRows-1)
            for r in range(self.__nRows):
                #self.__debug_stream("  a(x)  ",shifted_ax)
                #self.__debug_stream("  s[%d]  "%(r), [state[rbis][c] for rbis in range(self.__nRows)])
                res[r][c] = 0
                for rbis in range(self.__nRows):
                    res[r][c] ^= self.__polynomialsubfield.product(shifted_ax[rbis], sx[rbis][c])
                #self.__debug_stream("s'[%d][%d]"%(r,c), res[r][c])
                shifted_ax = shift(shifted_ax, -1)
        return res

class PolynomialField:
    def __init__(self,m):
        self.__m = m
    def product(self,a,b):
        '''multiplication of polynomials modulo an irreductible pylinomial of 
           field's degree. Over F_{2^8} this polynomial is 
           m(x) = x^8+x^4+x^3+x+1
           Input:
           Output:
        '''
        #FIXME: made sure about the irreductible polynomials used
        b_ = b
        xor = []
        a_i = [a]
        for i in range(binlen(b)):
            if b_&1:
                xor.append(a_i[len(a_i)-1])
            b_ >>= 1
            a_i.append(self.__xtime(a_i[len(a_i)-1]))
        r = 0
        for x in xor:
            r ^= x
        return r
    def __xtime(self,a):
        '''polynomial product by x reduced modulo m.
           Input: <integer> a (polynomial bit representation)
                  <integer> m (modulo polynomial)
           Output: <integer> a*x (mod m)
        '''
        a <<= 1
        if a & (1<<binlen(self.__m)-1): a ^= self.__m
        return a
#---- End Second descent level

#----# Third descent level
def shift(l,n):
    '''cyclic rotation of the list 'l' y 'n' elements. 
       Positive n's means left, negative n's means right.
       Input:
       Output:
    '''
    return l[n:] + l[:n]

class Word:
    def __init__(self,nRows,wordSize):
        self.__nRows = nRows
        self.__wordSize = wordSize
    def toList(self,superWord):
        '''Split an number in a set of integers with wordSize bits each
           Input: <integer> superWord
           Output: <integer array> wordsArray
           descent methods: []
           auxiliar methods: []
        '''
        wordsArray = []
        mask = int('0b'+'1'*self.__wordSize,2)
        for i in range(self.__nRows):
            wordsArray.append((superWord>>self.__wordSize*i)&mask)
        return wordsArray
    def fromList(self,wordsArray):
        '''Concatenate a set of integers (with wordSize bits each) into one 
           integer with size wordSize*len(wordList)
           Input: <integer array> wordsArray
           Output: <integer> superWord
           descent methods: []
           auxiliar methods: []
        '''
        superWord = 0
        for j in range(self.__nRows):
            superWord += wordsArray[j]<< self.__wordSize*(self.__nRows-j-1)
        return superWord

class Long:
    def __init__(self,wordSize):
        self.__wordSize = wordSize
    def toArray(self,input,length):
        '''Auxilliar method to unpack an integer to a set of smaller integers 
           in an array. The size of each of the integers in the set have the 
           wordSize
           Input: <integer>
           Output: <integer array>
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

    def fromArray(self,input,length):
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

class State:
    def __init__(self,nRows,nColumns):
        self.__nRows = nRows
        self.__nColumns = nColumns
    def fromArray(self,input):
        '''Given a one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
           Input: <integer array> 1d
           Output: <integer arrays> 2d
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
            debug_stream("state[%d]"%i, state[i])
        debug_stream("makeArray",state)
        return state

    def toArray(self,state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
           Input: <integer arrays> 2d
           Output: <integer array> 1d
        '''
        output = []
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        debug_stream("unmakeArray",output)
        return output
#---- End Third descent level