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
__copyright__ = "Copyright 2015 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

'''As a descendant level design, this file has the classes definitions of the
   levels above the Rijndael operations.
'''

from Logger import Logger as _Logger

binlen = lambda x: len(bin(x))-2


class Word:
    def __init__(self, nRows, wordSize):
        self.__nRows = nRows
        self.__wordSize = wordSize

    def toList(self, superWord):
        '''Split an number in a set of integers with wordSize bits each
           Input: <integer> superWord
           Output: <integer array> wordsArray
           descent methods: []
           auxiliar methods: []
        '''
        wordsArray = []
        mask = int('0b'+'1'*self.__wordSize, 2)
        for i in range(self.__nRows):
            wordsArray.append((superWord >> self.__wordSize*i) & mask)
        return wordsArray

    def fromList(self, wordsArray):
        '''Concatenate a set of integers (with wordSize bits each) into one
           integer with size wordSize*len(wordList)
           Input: <integer array> wordsArray
           Output: <integer> superWord
           descent methods: []
           auxiliar methods: []
        '''
        superWord = 0
        for j in range(self.__nRows):
            superWord += wordsArray[j] << self.__wordSize*(self.__nRows-j-1)
        return superWord


class Long:
    def __init__(self, wordSize):
        self.__wordSize = wordSize

    def toArray(self, input, length):
        '''Auxilliar method to unpack an integer to a set of smaller integers
           in an array. The size of each of the integers in the set have the
           wordSize
           Input: <integer>
           Output: <integer array>
        '''
        if input > int('0b'+('1'*length), 2):
            raise Exception("(long2array)", "Too big input for %d length"
                            % (length))
        o = []
        # cut the input blocs of the word size
        mask = (int('0b'+('1'*self.__wordSize), 2) << (length-self.__wordSize))
        for i in range(length/self.__wordSize):
            e = (input & mask) >> \
                (((length/self.__wordSize)-i-1)*self.__wordSize)
            o.append(int(e))
            mask >>= self.__wordSize
        return o

    def fromArray(self, input, length):
        '''Auxiliar method to pack an array of integers (with #wordSize bits)
           onto one integer.
           Input: <integer array>
           Output: <integer>
           descent methods: []
           auxiliar methods: []
        '''
        o = 0
        for i in range(length/self.__wordSize):
            o |= (input[i] << (((length/self.__wordSize)-i-1)*self.__wordSize))
        return o


def shift(l, n):
    # Binary doesn't need a class ----
    '''cyclic rotation of the list 'l' y 'n' elements.
       Positive n's means left, negative n's means right.
       Input:
       Output:
    '''
    return l[n:]+l[:n]


class State(_Logger):
    def __init__(self, nRows, nColumns, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
        self.__nRows = nRows
        self.__nColumns = nColumns

    def fromArray(self, input):
        '''Given a one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
           Input: <integer array> 1d
           Output: <integer arrays> 2d
        '''
        # FIXME: what happens if the size of input is not r*c? ----
        #        if exceeds, the rest are ignored;
        #        if not enough, empty cells
        state = [None] * self.__nRows
        for i in range(len(input)):
            row = i % self.__nRows
            if row == i:
                state[row] = [input[i]]
            else:
                state[row].append(input[i])
        for i in range(self.__nRows):
            self._debug_stream("state[%d]" % (i), state[i])
        self._debug_stream("makeArray", state)
        return state

    def toArray(self, state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
           Input: <integer arrays> 2d
           Output: <integer array> 1d
        '''
        output = []
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        self._debug_stream("unmakeArray", output)
        return output
