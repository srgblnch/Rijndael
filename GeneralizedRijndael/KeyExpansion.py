#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: KeyExpansion.pyx
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

from Logger import Logger
from SBox import SBox
from RoundConstant import RC
from ThirdLevel import Word,Long

class KeyExpansion(Logger):
    '''a Pseudo Random Generator that takes the key as a seed to expand
       it to generate all the subkeys need for each round of the Rijndael.
       Input: <integer> seed
       Output: <integer array> subkeys
    '''
    def __init__(self,key,
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None,
                 loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        self.__key=key
        self.__nRounds=nRounds
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__wordSize=wordSize
        self.__nKeyWords=nKeyWords
        self.__sbox=SBox(wordSize,loglevel=loglevel)
        self.__word=Word(nRows,wordSize)
        self.__keyExpanded=[None]*self.__nKeyWords
        self.debug_stream("key",key,operation="keyExpansion()\t")
        
        key=Long(self.__wordSize).toArray(key,self.__nKeyWords*self.__nRows*\
                                          self.__wordSize)
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
