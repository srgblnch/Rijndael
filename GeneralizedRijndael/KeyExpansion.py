#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: KeyExpansion.py
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

from Logger import Logger as _Logger
from SBox import SBox as _SBox
from RoundConstant import RC as _RC
from ThirdLevel import Word as _Word
from ThirdLevel import Long as _Long

class KeyExpansion(_Logger):
    '''a Pseudo Random Generator that takes the key as a seed to expand
       it to generate all the subkeys need for each round of the Rijndael.
       Input: <integer> seed
       Output: <integer array> subkeys
    '''
    def __init__(self,key,
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None,sboxCalc=False,
                 loglevel=_Logger._info, *args, **kwargs):
        super(KeyExpansion, self).__init__(*args, **kwargs)
        self.__key=key
        self.__nRounds=nRounds
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__wordSize=wordSize
        self.__nKeyWords=nKeyWords
        self.__sbox=_SBox(wordSize,sboxCalc,loglevel=loglevel)
                         #,useCalc=True)
        self.__word=_Word(nRows,wordSize)
        self.__keyExpanded=[None]*self.__nKeyWords
        self._debug_stream("key",key,operation="keyExpansion()\t")
        
        key=_Long(self.__wordSize).toArray(key,self.__nKeyWords*self.__nRows*\
                                          self.__wordSize)
        self._debug_stream("key array",key,operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            self.__keyExpanded[i]=_Word(self.__nRows,
                    self.__wordSize).fromList(key[(self.__nRows*i):\
                                                (self.__nRows*i)+self.__nRows])
        i=self.__nKeyWords
        while (i<(self.__nColumns*(self.__nRounds+1))):
            self._debug_stream("i",i,operation='keyExpansion()\t')
            temp=self.__keyExpanded[i-1]
            self._debug_stream("temp",temp,operation='keyExpansion()\t')
            if (i%self.__nKeyWords==0):
                rotWord=self.__rotWord(temp)
                self._debug_stream("rotWord",
                                  rotWord,operation='keyExpansion()\t')
                subWord=self.__subWord(rotWord)
                self._debug_stream("subWord",
                                  subWord,operation='keyExpansion()\t')
                Rcon=_Word(self.__nRows,
                       self.__wordSize).fromList([_RC[i/self.__nKeyWords],0,0,0])
                subWord^=Rcon
                self._debug_stream("Rcon",Rcon,operation='keyExpansion()\t')
                self._debug_stream("subWord with Rcon",subWord,
                                  operation='keyExpansion()\t')
            elif i%self.__nKeyWords==4:
                subWord=self.__subWord(subWord)
                self._debug_stream("subWord",
                                  subWord,operation='keyExpansion()\t')
            else:
                subWord=temp
            self._debug_stream("w[i-Nk]",self.__keyExpanded[i-self.__nKeyWords],
                              operation='keyExpansion()\t')
            self.__keyExpanded.append(self.__keyExpanded[i-self.__nKeyWords]\
                                      ^subWord)
            self._debug_stream("w[i]",self.__keyExpanded[i],
                              operation='keyExpansion()\t')
            i+=1
        self._debug_stream("keyExpanded",self.__keyExpanded,
                          operation="keyExpansion()\t")
        self._debug_stream("size of key expanded %d"%len(self.__keyExpanded))
        
    def getKey(self):
        return self.__keyExpanded
    def getSubKey(self,start,end):
        self._debug_stream("Requested part of the key expanded. k[%d:%d] = %s"
                           %(start,end,self.__keyExpanded[start:end]))
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
        wordArray = self.__sbox.transform(wordArray)
        wordArray.reverse()#---- FIXME: Where is this in the fips pub-197?
        return self.__word.fromList(wordArray)
