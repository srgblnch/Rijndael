#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: GeneralizedRijndael.pyx
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
from version import *

binlen=lambda x: len(bin(x))-2

debug=False#by default
#debug = True

def __version__():
    return '%d.%d.%d-%d'%(MAJOR_VERSION,MINOR_VERSION,
                          BUILD_VERSION,REVISION_VERSION),

class Logger:
    def __init__(self,debug=False):
        self._debug = [debug]
    def debug_stream(self,logtext,data=None,round=None,operation=None):
        if any(self._debug):
            msg=""
            if not round==None: msg+="Round[%d];"%round
            if not operation==None: msg+="%s:"%operation
            msg+=logtext
            if not data==None:
                if type(data) in [int,long]: msg+="=%s"%hex(data)
                elif type(data)==list:
                    msg+="=["
                    for element in data:
                        if type(element) in [int,long]: msg+="%4s,"%hex(element)
                        elif type(element)==list:
                            msg+="["
                            for subelem in element: msg+="%4s,"%hex(subelem)
                            msg=msg[:len(msg)-1]+"],"
                        else: msg+="%s,"%element
                    msg=msg[:len(msg)-1]+"]"
                else: msg+="=%s"%(data)
            print msg

class GeneralizedRijndael(Logger):
    def __init__(self,key,debug=[False,#keyExpansion
                                 False,#subBytes
                                 False,#shiftRows
                                 False,#mixColumns
                                 False],#addRoundKey
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None):
        if type(debug) == list:
            if len(debug) == 5:
                self._debug = debug
            else:
                self._debug = [any(debug)]*5
        elif type(debug) == bool:
            self._debug = [debug]*5
        else:
            self._debug = [False]*5
        self.__nRounds=nRounds#Num of encryption rounds {10,12,14}
        self.__nRows=nRows#Num of rows in the rectangular arrangement
        self.__nColumns=nColumns#Num of cols in the rectangular arrangement
        self.__wordSize=wordSize#in bits, AES is 8 bits word
        if nKeyWords==None:
            self.__nKeyWords=nColumns
        else:
            self.__nKeyWords=nKeyWords#Usually {4,6,8}
        self.debug_stream("Rijndael(%d,%d,%d,%d): block=%dbits key=%dbits"
                          %(self.__nRounds,self.__nRows,self.__nColumns,
                            self.__wordSize,
                            self.__nColumns*self.__nRows*self.__wordSize,
                            self.__nKeyWords*self.__nRows*self.__wordSize))
        self._keyExpander = KeyExpander(key,self.__nRounds,self.__nRows,
                                        self.__nColumns,self.__wordSize,
                                        self.__nKeyWords,debug=self._debug[0])
        self._subBytes = SubBytes(wordSize,debug=self._debug[1])
        self._shiftRows = ShiftRows(nRows,debug=self._debug[2])
        self._mixColumns = MixColumns(nRows,nColumns,wordSize,
                                      debug=self._debug[3])
        self._addRoundKey = AddRoundKey(nRows,nColumns,wordSize,
                                        debug=self._debug[4])

    def cipher(self,plain):
        '''plain (1d array) is copied to state matrix.
           After the inicial round addition, the state is transformed by the
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
           Input: <integer> plainText
           Output: <integer> cipherText
        '''
        self.debug_stream("plaintext",plain)
        plain=Long(self.__wordSize).toArray(plain,self.__nColumns*self.__nRows*\
                                            self.__wordSize)
        #---- TODO: check the plain have the size to be ciphered
        self.debug_stream("plaintext array",plain)
        #---- FIXME: State should be protected in memory 
        #            to avoid side channel attacks
        state=State(self.__nRows,self.__nColumns,
                    debug=self._debug).fromArray(plain)
        self.debug_stream("state",state)
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey(0,self.__nColumns))#w[0,Nb-1]
        self.debug_stream("state",state,0,"cipher->addRoundKey()\t")
        for r in range(1,self.__nRounds):#[1..Nr-1] step 1
            state=self._subBytes.do(state)
            self.debug_stream("state",state,r,"cipher->subBytes()\t")
            state=self._shiftRows.do(state)
            self.debug_stream("state",state,r,"cipher->shiftRows()\t")
            state=self._mixColumns.do(state)
            self.debug_stream("state",state,r,"cipher->mixColumns()\t")
            state=self._addRoundKey.do(state,\
                    self._keyExpander.getSubKey((r*self.__nColumns),
                                                (r+1)*(self.__nColumns)))
            self.debug_stream("state",state,r,"cipher->addRoundKey()\t")
        state=self._subBytes.do(state)
        self.debug_stream("state",state,self.__nRounds,"cipher->subBytes()\t")
        state=self._shiftRows.do(state)
        self.debug_stream("state",state,self.__nRounds,"cipher->shiftRows()\t")
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),
                                            (self.__nRounds+1)*\
                                            (self.__nColumns)))
        self.debug_stream("state",state,
                          self.__nRounds,"cipher->addRoundKey()\t")
        cipher=State(self.__nRows,self.__nColumns,
                     debug=self._debug).toArray(state)
        self.debug_stream("ciphertext array",cipher)
        cipher=Long(self.__wordSize).fromArray(cipher,self.__nColumns*\
                                               self.__nRows*self.__wordSize)
        self.debug_stream("ciphertext",cipher)
        return cipher

    def decipher(self,cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
           Input: <integer> cipherText
           Output: <integer> plainText
        '''
        self.debug_stream("ciphered",cipher)
        cipher=Long(self.__wordSize).toArray(cipher,self.__nColumns*\
                                             self.__nRows*self.__wordSize)
        #---- TODO: check the cipher have the size to be deciphered
        self.debug_stream("ciphered array",cipher)
        #---- FIXME: State should be protected in memory 
        #            to avoid side channel attacks
        state=State(self.__nRows,self.__nColumns,
                    debug=self._debug).fromArray(cipher)
        self.debug_stream("state",state)
        state=self._addRoundKey.do(state,\
                self._keyExpander.getSubKey((self.__nRounds*self.__nColumns),
                                            (self.__nRounds+1)*\
                                            (self.__nColumns)))
        self.debug_stream("state",state,self.__nRounds,
                          "decipher->addRoundKey()\t")
        for r in range(self.__nRounds-1,0,-1):#[Nr-1..1] step -1
            state=self._shiftRows.invert(state)
            self.debug_stream("state",state,r,"decipher->invShiftRows()\t")
            state=self._subBytes.invert(state)
            self.debug_stream("state",state,r,"decipher->invSubBytes()\t")
            state=self._addRoundKey.do(state,
                    self._keyExpander.getSubKey((r*self.__nColumns),
                                                (r+1)*(self.__nColumns)))
            self.debug_stream("state",state,r,"decipher->addRoundKey()\t")
            state=self._mixColumns.invert(state)
            self.debug_stream("state",state,r,"decipher->invMixColumns()\t")
        state=self._shiftRows.invert(state)
        self.debug_stream("state",state,0,"decipher->invShiftRows()\t")
        state=self._subBytes.invert(state)
        self.debug_stream("state",state,0,"decipher->invSubBytes()\t")
        state=self._addRoundKey.do(state,
                                   self._keyExpander.getSubKey(0,
                                                               self.__nColumns))
        self.debug_stream("state",state,0,"decipher->addRoundKey()\t")
        plain=State(self.__nRows,self.__nColumns,
                    debug=self._debug).toArray(state)
        self.debug_stream("deciphered array",plain)
        plain=Long(self.__wordSize).fromArray(plain,self.__nColumns*\
                                              self.__nRows*self.__wordSize)
        self.debug_stream("deciphered",plain)
        return plain
    #----# test methods
    def unitTestCompare(self,calculation,expected):
        '''
           Input:
           Output:
           descent methods: []
           auxiliar methods: []
        '''
        if not type(calculation)==type(expected):
            print("Ooh!")
            return False
        if type(calculation)==list:
            for i in range(len(calculation)):
                recursive=self.unitTestCompare(calculation[i],expected[i])
                if recursive==False: return False
            return True
        elif type(calculation) in [int,long]:
            if calculation==expected: return True
            else: return False
    #---- End test methods

#----# First descent level
class KeyExpander(Logger):
    def __init__(self,key,nRounds,nRows,nColumns,wordSize,nKeyWords,debug=False):
        '''a Pseudo Random Generator that takes the key as a seed to expand
           it to generate all the subkeys need for each round of the Rijndael.
           Input: <integer> seed
           Output: <integer array> subkeys
        '''
        self._debug = [debug]
        self.__key=key
        self.__nRounds=nRounds
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__wordSize=wordSize
        self.__nKeyWords=nKeyWords
        self.__sbox=SBox(wordSize)
        self.__word=Word(nRows,wordSize)
        self.__keyExpanded=[None]*self.__nKeyWords

        self.debug_stream("key",key,operation="keyExpansion()\t")
        key=Long(self.__wordSize).toArray(key,self.__nKeyWords*self.__nRows*\
                                          self.__wordSize)
        self.__keyExpanded=[None]*self.__nKeyWords
        self.debug_stream("key array",key,operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            self.__keyExpanded[i]=Word(self.__nRows,
                    self.__wordSize).fromList(key[(self.__nRows*i):\
                                                 (self.__nRows*i)+self.__nRows])
        i=self.__nKeyWords
        while (i<(self.__nColumns*(self.__nRounds+1))):
            self.debug_stream("i",i,operation='keyExpansion()\t')
            temp=self.__keyExpanded[i-1]
            self.debug_stream("temp",temp,operation='keyExpansion()\t')
            if (i%self.__nKeyWords==0):
                rotWord=self.__rotWord(temp)
                self.debug_stream("rotWord",
                                  rotWord,operation='keyExpansion()\t')
                subWord=self.__subWord(rotWord)
                self.debug_stream("subWord",
                                  subWord,operation='keyExpansion()\t')
                Rcon=Word(self.__nRows,
                       self.__wordSize).fromList([RC[i/self.__nKeyWords],0,0,0])
                subWord^=Rcon
                self.debug_stream("Rcon",Rcon,operation='keyExpansion()\t')
                self.debug_stream("subWord with Rcon",subWord,
                                  operation='keyExpansion()\t')
            elif i%self.__nKeyWords==4:
                subWord=self.__subWord(subWord)
                self.debug_stream("subWord",
                                  subWord,operation='keyExpansion()\t')
            else:
                subWord=temp
            self.debug_stream("w[i-Nk]",self.__keyExpanded[i-self.__nKeyWords],
                              operation='keyExpansion()\t')
            self.__keyExpanded.append(self.__keyExpanded[i-self.__nKeyWords]\
                                      ^subWord)
            self.debug_stream("w[i]",self.__keyExpanded[i],
                              operation='keyExpansion()\t')
            i+=1
        self.debug_stream("keyExpanded",self.__keyExpanded,
                          operation="keyExpansion()\t")
        self.debug_stream("size of key expanded %d"%len(self.__keyExpanded))

    def getKey(self):
        return self.__keyExpanded
    def getSubKey(self,start,end):
        return self.__keyExpanded[start:end]
    def __rotWord(self,w):
        '''Used in the key expansion. A cyclic shift of the bytes in the word.
           Input: <integer> w (with length wordSize)
           Output: <integer> w (modified)
        '''
        #Parentesis are very important
        wordMask=int('0b'+('1'*self.__wordSize)+('0'*(self.__wordSize*\
                                                      (self.__nColumns-1))),2)
        shiftMask=int('0b'+('1'*(self.__wordSize*(self.__nColumns))),2)
        return (((w&wordMask)>>(self.__wordSize*(self.__nRows-1)))|\
                ((w<<self.__wordSize)&shiftMask))

    def __subWord(self,word):
        '''Used in the key expansion. Apply a table lookup (sbox) to the set
           of words.
           Input: <integer> word
           Output: <integer> word
        '''
        wordArray=self.__word.toList(word)
        self.__sbox.transform(wordArray)
        wordArray.reverse()#---- FIXME: Where is this in the fips pub-197?
        return self.__word.fromList(wordArray)

class SubBytes(Logger):
    '''This class is made to do the subBytes Rijndael's non-linear 
       substitution to provide confusion to the ciphertext, and its inverse.
       It uses a secondary object SBox as a builder pattern to allow the 
       transformation from this operation.
       FIXME: The precalculated SBoxes shall be replaced by the calculations
       themselves specially to allow arbitrary word sizes and not only the
       original 8 bits and the two included here for 2 and 4 bits.
    '''
    def __init__(self,wordSize,debug=False):
        self._debug = [debug]
        self.__sbox=SBox(wordSize)
    def do(self,input):
        return self.__sbox.transform(input)
    def invert(self,input):
        return self.__sbox.transform(input,invert=True)
        #It's the same but different sbox

class ShiftRows(Logger):
    def __init__(self,nRows,debug=False):
        self._debug = [debug]
        self.__nRows=nRows
    def do(self,input):
        '''One of the round transformation methods.
           cyclical left shift of the row 'i' of the state matrix by 'i' 
           positions s[r][c] = s[r][c+shift(r,nColumns) mod nColumns]
           for 0<r<nRows and 0<=c<nColumns.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output=[]
        for i in range(self.__nRows):
            output.append(shift(input[i],i))
        return output
    def invert(self,input):
        '''Inverse of the shiftRows() method.
           Input: <integer arrays> state
           Output: <integer arrays> state (modified)
        '''
        output=[]
        for i in range(self.__nRows):
            output.append(shift(input[i],-i))
        return output

class MixColumns:
    def __init__(self,nRows,nColumns,wordSize,debug=False):
        self._debug = [debug]
        #---- FIXME: refactor this horrible if
        if wordSize==8:
            if nRows==4:
                #MDS matrices (Maximum Distance Separable)
                self.__cx=[0x3,0x1,0x1,0x2]
                self.__dx=[0xB,0xD,0x9,0xE]#c(x) \otimes d(x) = 1 (mod m)
            elif nRows==3:
                self.__cx=[0xD,0x1,0x1]#---- FIXME: unknown
                self.__dx=[0x3C,0xAA,0x3C]#---- FIXME: unknown
            elif nRows==2:
                self.__cx=[0x2,0x3]#---- FIXME: unknown
                self.__dx=[0x2,0x3]#---- FIXME: unknown
            polynomialModule=0b100011011
        elif  wordSize==4:
            if nRows==4:
                self.__cx=self.__dx=[0,0,0,0]#---- FIXME: unknown
            elif nRows==3:
                self.__cx=self.__dx=[0,0,0]#---- FIXME: unknown
            elif nRows==2:
                self.__cx=self.__dx=[0,0]#---- FIXME: unknown
            polynomialModule=0b10000
        elif  wordSize==2:
            if nRows==4:
                self.__cx=self.__dx=[0x3,0x1,0x1,0x2]#---- FIXME: unknown
            elif nRows==3:
                self.__cx=self.__dx=[0,0,0]#---- FIXME: unknown
            elif nRows==2:
                self.__cx=self.__dx=[0x2,0x3]#---- FIXME: unknown
            polynomialModule=0b100
        self.__polynomialRing=PolynomialRing(nRows,nColumns,polynomialModule)
    def do(self,input):
        return self.__polynomialRing.product(self.__cx,input)
    def invert(self,input):
        return self.__polynomialRing.product(self.__dx,input)

class AddRoundKey:
    def __init__(self,nRows,nColumns,wordSize,debug=False):
        self._debug = [debug]
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__word=Word(nRows,wordSize)
    def do(self,input,subkey):
        '''One of the round transformation methods.
           The round key (from the PRG) list of arrays (can be thougth as a
           matrix), is bitwise XORted with the state matrix.
           Input: <integer arrays> state, subkey
           Output: <integer arrays> state (modified)
        '''
        output=input
        for j in range(self.__nColumns):
            byteSubkey=self.__word.toList(subkey[j])
            byteSubkey.reverse()
            for i in range(self.__nRows):
                bar=output[i][j]
                bar^=byteSubkey[i]
                output[i][j]=bar
        return output

#---- End First descent level

#----# Second descent level
class SBox:
    '''This class is used from the subBytes rijndael's transformation. But it 
       is using an auxiliar python source file who have stored the original 
       sbox and its inverse, for 8 bits word size, as well as it have two 
       other pairs of sboxes for word size 2 and 4 made on this development.
    '''
    def __init__(self,wordSize,useCalc=False):
        #---- TODO: this must be able to be modified to use a sbox as a table 
        #           or as the pure calculations
        self._useCalc = useCalc
        if self._useCalc:
            self._field = PolynomialField(wordSize)
        else:
            self.__wordSize=wordSize
            if wordSize==8:
                self._sbox=sbox_word8b
                self._sbox_inverted=sbox_word8b_inverted
            elif  self.__wordSize==4:
                self._sbox=sbox_word4b
                self._sbox_inverted=sbox_word4b_inverted
            elif  self.__wordSize==2:
                self._sbox=sbox_word2b
                self._sbox_inverted=sbox_word2b_inverted
            if not (hasattr(self,"_sbox") or hasattr(self,"_sbox_inverted")):
                raise Exception("(__init__)","There is no Sbox for %d wordsize"\
                                %(self.__wordSize))
    def transform(self,state,invert=False):
        '''Given the content of one cell of the state matrix, 'divide' in 2 
           halfs. The upper is understood as the row and the lower as the 
           column in the sbox. The sbox is a paramenter because the 
           transformation use one sbox or its invers, but the procedure is 
           the same.
           Input:
           Output:
        '''
        if self._useCalc:
            raise Exception("SBox transformation with calculations "\
                            "not supported yet!")
            if invert: sbox=self._invertsbox_call_
            else: sbox=self._sbox_call_
            for i in range(len(state)):
                if type(state[i])==list:
                    for j in range(len(state[i])):
                        state[i][j] = sbox(state[i][j])
                else:
                    state[i] = sbox(state[i])
        else:
            if invert: sbox=self._sbox_inverted
            else: sbox=self._sbox
            for i in range(len(state)):
                if type(state[i])==list:
                    for j in range(len(state[i])):
                        r,c=self.__hexValue2MatrixCoords(state[i][j])
                        state[i][j]=sbox[r][c]
                else:
                    r,c=self.__hexValue2MatrixCoords(state[i])
                    state[i]=sbox[r][c]
        return state
    def __hexValue2MatrixCoords(self,value):
        '''Split the input in to equal halfs that will be used as coordinates
           in the sbox transformations.
           Input: <integer> value
           Output: <integer> row, <integer> column
        '''
        if self.__wordSize%2==1:
            raise Exception("(__hexValue2MatrixCoords)","Matrix coordinates "\
                            "impossible for an odd %d wordsize"
                            %(self.__wordSize))
        cmask='0b'+'1'*(self.__wordSize/2)
        rmask='0b'+'1'*(self.__wordSize/2)+'0'*(self.__wordSize/2)
        c=(value&int(cmask,2))
        r=(value&int(rmask,2))>>(self.__wordSize/2)
        return r,c
    def _sbox_call_(self,value):
        g = self._field.multiplicativeInverse(value)
        f = self._field.affineTransformation(g)
        return f
    def _invertsbox_call_(self,value):
        g = self._field.multiplicativeInverse(value)
        f = self._field.invertAffineTransformation(g)
        return f

#RoundConstant
# RC[1] = 0x01
# RC[i] = x * RC[i-1] = x**(i-1)
RC=[
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
class RoundConstant:
    ''''An instance of this class is used in the keyExpansion to get back the
        x^(i-1) power of x, where x is denoted 0x02 in GF(2^8)
        i, starts at 1, not 0.
    '''
    def __init__(self,nRows,nColumns,wordSize):
        #---- FIXME:why this has this initial unused 0x8D?
        self.__rcon=[0x8D,0x01]
        self.__polynomialsubfield=PolynomialField(wordSize)
        self.__calculateUntil(nColumns*(nRows+1))
    def __calculateUntil(self,n):
        if n<len(self.__rcon):
            for i in range(len(self.__rcon),n):
                self.__rcon.\
                   append(self.__polynomialsubfield.\
                             xtime(self.__rcon[len(self.__rcon)-1]))
    def get(self,i):
        if len(self.__rcon)<i:
            self.__calculateUntil(i)
        return [self.__rcon[i],0,0,0]

class PolynomialRing:
    '''This represents a polynomial over (GF(2^n))^l, with a modulo polynomial 
       composed (decomposable in roots) this becomes a algebraic ring.
       The coefficients on this polynomial ring are elements of a polynomial field.
    '''
    def __init__(self,nRows,nColumns,wordSize):
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__polynomialsubfield=PolynomialField(wordSize)
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
        res=deepcopy(sx)#---- FIXME: #[[0]*self.__nRows]*self.__nColumns
        for c in range(self.__nColumns):
            shifted_ax=shift(ax,self.__nRows-1)
            for r in range(self.__nRows):
                res[r][c]=0
                for rbis in range(self.__nRows):
                    res[r][c]^=self.__polynomialsubfield.\
                                          product(shifted_ax[rbis],sx[rbis][c])
                shifted_ax=shift(shifted_ax,-1)
        return res

PolynomialFieldModulo = {2:0x07,#z^2+z+1
                         3:0x0B,#z^3+z+1
                         4:0x13,#z^4+z+1
                         5:0x25,#z^5+z^2+1
                         6:0x43,#z^6+z+1
                         7:0x83,#z^7+z+1
                         8:0x11B,#z^8+z^4+z^3+z+1 the Rijndael's original
                         9:0x203,#z^9+z+1
                         10:0x409,#z^10+z^3+1
                         11:0x805,#z^11+z^2+1
                         12:0x1009,#z^12+z^3+1
                         13:0x201B,#z^13+z^4+z^3+z+1
                         14:0x4021,#z^14+z^5+1
                         15:0x8003,#z^15+z+1
                         16:0x1002B,#z^16+z^5+z^3+z+1
                        }[wordSize]

class PolynomialField:
    '''This represents a polynomial over (GF(2^n) with a degree at most 2^{n}-1
       Because the polynomial modulo is prime (it is a root) this 
       describes an algebraic field.
    '''
    def __init__(self,degree):
        self._degree = degree
        self._modulo = PolynomialFieldModulo[degree]
    def product(self,a,b):
        '''multiplication of two polynomials reduced modulo m(z).
           Input: <integer> a,b (polynomial bit representations)
                  <integer> m (modulo polynomial)
           Output: <integer> r = a*b (mod m)
        '''
        b_=b
        xor=[]
        a_i=[a]
        for i in range(binlen(b)):
            if b_&1:
                xor.append(a_i[len(a_i)-1])
            b_>>=1
            a_i.append(self.xtime(a_i[len(a_i)-1]))
        r=0
        for x in xor:
            r^=x
        return r
    def xtime(self,a):
        '''polynomial product by x reduced modulo m.
           Input: <integer> a (polynomial bit representation)
                  <integer> m (modulo polynomial)
           Output: <integer> a*x (mod m)
        '''
        a<<=1
        if a&(1<<binlen(self._modulo)-1): a^=self._modulo
        return a
    def multiplicativeInverse(self,value):
        '''Multiplicative inverse based on ...
           Input: <integer> a (polynomial bit representation)
                  <integer> m (modulo polynomial)
           Output: <integer> a^-1: a*a^-1 = 1 (mod m)
           This it the first of the two transformations for the SBoxes in the 
           subBytes operation, the one called called g.
        '''
        gcd,x,y = self._egcd(value, self._modulo)
        if gcd != 1:
            raise Exception("The inverse of %s modulo %s doens't exist!"%(value,self._modulo))
        else:
            return x%m
    def affineTransformation(self,value):
        '''Second of the transformation, called f.
        '''
        pass
    def _egcd(self,a,b):
        '''Extended Euclidean Algorithm
        '''
        x,y,u,v = 0,1,1,0
        while a != 0:
            q,r = b/a,b%a
            m,n = x-u*q,y-v*q
            b,a,x,y,u,v=a,r,u,v,m,n
        gcd = b
        return gcd,x,y
#---- End Second descent level

#----# Third descent level
def shift(l,n):
    #---- Binary doesn't need a class
    '''cyclic rotation of the list 'l' y 'n' elements. 
       Positive n's means left, negative n's means right.
       Input:
       Output:
    '''
    return l[n:]+l[:n]

class Word:
    def __init__(self,nRows,wordSize):
        self.__nRows=nRows
        self.__wordSize=wordSize
    def toList(self,superWord):
        '''Split an number in a set of integers with wordSize bits each
           Input: <integer> superWord
           Output: <integer array> wordsArray
           descent methods: []
           auxiliar methods: []
        '''
        wordsArray=[]
        mask=int('0b'+'1'*self.__wordSize,2)
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
        superWord=0
        for j in range(self.__nRows):
            superWord+=wordsArray[j]<<self.__wordSize*(self.__nRows-j-1)
        return superWord

class Long:
    def __init__(self,wordSize):
        self.__wordSize=wordSize
    def toArray(self,input,length):
        '''Auxilliar method to unpack an integer to a set of smaller integers
           in an array. The size of each of the integers in the set have the
           wordSize
           Input: <integer>
           Output: <integer array>
        '''
        if input>int('0b'+('1'*length),2):
            raise Exception("(long2array)","Too big input for %d lenght"
                            %(length))
        o=[]
        #cut the input blocs of the word size
        mask=(int('0b'+('1'*self.__wordSize),2)<<(length-self.__wordSize))
        for i in range(length/self.__wordSize):
            e=(input&mask)>>(((length/self.__wordSize)-i-1)*self.__wordSize)
            o.append(int(e))
            mask>>=self.__wordSize
        return o

    def fromArray(self,input,length):
        '''Auxiliar method to pack an array of integers (with #wordSize bits)
           onto one integer.
           Input: <integer array>
           Output: <integer>
           descent methods: []
           auxiliar methods: []
        '''
        o=0
        for i in range(length/self.__wordSize):
            o|=(input[i]<<(((length/self.__wordSize)-i-1)*self.__wordSize))
        return o

class State(Logger):
    def __init__(self,nRows,nColumns,debug=False):
        self._debug = debug
        self.__nRows=nRows
        self.__nColumns=nColumns
    def fromArray(self,input):
        '''Given a one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
           Input: <integer array> 1d
           Output: <integer arrays> 2d
        '''
        #---- FIXME: what happens if the size of input is not r*c?
        #       if exceeds, the rest are ignored;
        #       if not enough, empty cells
        state=[None]*self.__nRows
        for i in range(len(input)):
            row=i%self.__nRows
            if row==i:
                state[row]=[input[i]]
            else:
                state[row].append(input[i])
        for i in range(self.__nRows):
            self.debug_stream("state[%d]"%i,state[i])
        self.debug_stream("makeArray",state)
        return state

    def toArray(self,state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
           Input: <integer arrays> 2d
           Output: <integer array> 1d
        '''
        output=[]
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        self.debug_stream("unmakeArray",output)
        return output
#---- End Third descent level

if __name__ == "__main__":
    #---- TODO: introduce parameters to:
    #           - define parameters to use and use random input and key.
    #           - allow to setup by params the input and/or the key, and
    #           - operations to do: cipher and/or decipher
    print("Nothing (yet) to do with this module execution.")
    #---- TODO: 
