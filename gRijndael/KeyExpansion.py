# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2013 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

from Logger import Logger as _Logger, _DEBUG
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
    def __init__(self, key,
                 nRounds=10, nRows=4, nColumns=4, wordSize=8,  # stardard aes
                 nKeyWords=None, loglevel=_Logger._info, *args, **kwargs):
        super(KeyExpansion, self).__init__(loglevel, *args, **kwargs)
        self.__key = key
        self.__nRounds = nRounds
        self.__nRows = nRows
        self.__nColumns = nColumns
        self.__wordSize = wordSize
        if nKeyWords:
            self.__nKeyWords = nKeyWords
        else:
            self.__nKeyWords = nColumns
        self.__sbox = _SBox(self.__wordSize, loglevel=loglevel)
        self.__word = _Word(self.__nRows, self.__wordSize)
        self.__keyExpanded = [None]*self.__nKeyWords
        self._debug_stream("key", key, operation="keyExpansion()\t")
        try:
            key = _Long(self.__wordSize).toArray(key,
                                                 self.__nKeyWords *
                                                 self.__nRows *
                                                 self.__wordSize)
        except:
            raise Exception("Key length doesn't fit with the matrix size")
        self._debug_stream("key array", key, operation="keyExpansion()\t")
        for i in range(self.__nKeyWords):
            subkey = key[(self.__nRows*i):(self.__nRows*i)+self.__nRows]
            self.__keyExpanded[i] = \
                _Word(self.__nRows, self.__wordSize).fromList(subkey)
        i = 0
        while (i < (self.__nKeyWords*(self.__nRounds+1))):
            self._debug_stream("i = %d" % (i), operation='keyExpansion()\t')
            if i < self.__nKeyWords:
                self._debug_stream("\tw[%d]" % (i), self.__keyExpanded[i],
                                   operation='keyExpansion()\t')
            else:
                subWord = self.__keyExpanded[i-1]
                self._debug_stream("\tw[i-1]=w[%d]" % (i-1), subWord,
                                   operation='keyExpansion()\t')
                if (i % self.__nKeyWords == 0):
                    rotWord = self.__rotWord(subWord)
                    subWord = self.__subWord(rotWord)
                    Rcon = self.__Rcon(i)
                    subWord = self.__xor(subWord, Rcon,
                                         "subWord", "Rcon", "subWord")
                elif (self.__nKeyWords > 6) and (i % self.__nKeyWords == 4):
                    subWord = self.__subWord(subWord)
                self._debug_stream("\tw[i-Nk]=w[%d]" % (i-self.__nKeyWords),
                                   self.__keyExpanded[i-self.__nKeyWords],
                                   operation='keyExpansion()\t')
                self.__keyExpanded.append(self.__xor(self.__keyExpanded
                                                     [i-self.__nKeyWords],
                                                     subWord, "w[%d]"
                                                     % (i-self.__nKeyWords),
                                                     "subWord", "w[%d]" % (i)))
            i += 1
        self._debug_stream("keyExpanded", self.__keyExpanded,
                           operation="keyExpansion()\t")
        self._debug_stream("size of key expanded %d"
                           % (len(self.__keyExpanded)))

    def __str__(self):
        parentesis = "%d, %d, %d, %d" % (self.__nRounds, self.__nRows,
                                         self.__nColumns, self.__wordSize)
        if self.__nKeyWords != self.__nColumns:
            parentesis += ", %d" % (self.__nKeyWords)
        parentesis += ", %s" % (self.logLevelStr)
        return "KeyExpansion(%s)" % (parentesis)

    def __repr__(self):
        return "%s" % (self.__str__())

    def getKey(self):
        return self.__keyExpanded

    def getSubKey(self, start, end):
        subkey = self.__keyExpanded[start:end]
        ashexlist = ["%s" % hex(each) for each in subkey]
        self._debug_stream("Requested part of the key expanded. k[%d:%d] = %s"
                           % (start, end, ashexlist))
        return self.__keyExpanded[start:end]

    def __rotWord(self, w):
        '''Used in the key expansion. A cyclic shift of the bytes in the word.
           Input: <integer> w (with length wordSize)
           Output: <integer> w (modified)
        '''
        # Parentesis are very important
        wordMask = int('0b'+('1'*self.__wordSize) +
                       ('0'*(self.__wordSize*(self.__nColumns-1))), 2)
        shiftMask = int('0b'+('1'*(self.__wordSize*(self.__nColumns))), 2)
        rotWord = (((w & wordMask) >> (self.__wordSize * (self.__nRows-1))) |
                   ((w << self.__wordSize) & shiftMask))
        self._debug_stream("\trotWord(%s)" % (hex(w)), rotWord,
                           operation='keyExpansion()\t')
        return rotWord

    def __subWord(self, word):
        '''Used in the key expansion. Apply a table lookup (sbox) to the set
           of words.
           Input: <integer> word
           Output: <integer> word
        '''
        wordArray = self.__word.toList(word)
        wordArray = self.__sbox.transform(wordArray)
        wordArray.reverse()  # FIXME: Where is this in the fips pub-197?
        subWord = self.__word.fromList(wordArray)
        self._debug_stream("\tsubWord(%s)" % (hex(word)), subWord,
                           operation='keyExpansion()\t')
        return subWord

    def __Rcon(self, i):
        rc = [0]*self.__nRows
        rc[0] = _RC[i/self.__nKeyWords]
        Rcon = _Word(self.__nRows, self.__wordSize).fromList(rc)
        self._debug_stream("\tRcon[%d]" % (i), Rcon,
                           operation='keyExpansion()\t')
        return Rcon

    def __xor(self, a, b, aName=None, bName=None, cName=None):
        c = a ^ b
        self._debug_stream("\t%s=%s^%s=%s^%s"
                           % (cName, aName, bName, hex(a), hex(b)), c,
                           operation='keyExpansion()\t')
        return c
