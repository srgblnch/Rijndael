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

import sys

from Logger import Logger as _Logger
from Logger import debug, trace
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
        Object that, once created and initialised (parameters and secret key)
        can receive the request to cipher some input or decipher it.
        
        Parameters:
        - key: <mandatory> integer that will be used as a key. It cannot be
               bigger than the key size that will be build.
        - nRounds: <default:based on the other parameters>
        - nRows: <default:4>
        - nColumns: <default:4>
        - wordSize: <default:8>
        - kKeycolumns: <default:nColumns>
        
        Extra parameters:
        - sboxCalc: <default:True>
        - loglevel:: <default:info>
    '''
    def __init__(self, key,
                 nRounds=None, nRows=4, nColumns=4, wordSize=8,  # stardard aes
                 nKeyColumns=None, sboxCalc=True,
                 loglevel=_Logger._info, *args, **kwargs):
        super(GeneralizedRijndael, self).__init__(*args, **kwargs)
        # Num of encryption rounds {10,12,14}
        if nRounds is None:
            if nKeyColumns is not None:
                self.__nRounds = max(nKeyColumns, nColumns) + 6
            else:
                self.__nRounds = nColumns + 6
        else:
            self.__nRounds = nRounds
        # Num of rows in the rectangular arrangement
        self.__nRows = nRows
        # Num of cols in the rectangular arrangement
        self.__nColumns = nColumns
        # in bits, AES is 8 bits word
        self.__wordSize = wordSize
        if nKeyColumns is None:
            self.__nKeyColumns = nColumns
        else:
            self.__nKeyColumns = nKeyColumns  # Usually {4,6,8}
        minRounds = max(self.__nKeyColumns, self.__nColumns) + 6
        if self.__nRounds < minRounds:
            self._warning_stream(" Perhaps this is not enough rounds: "
                                 "max(N_k,N_c)+6 = max(%d,%d)+6 = %d"
                                 % (self.__nKeyColumns, self.__nColumns,
                                    minRounds))
        self._debug_stream("Initialising GeneralizedRijndael "
                           "(%d,%d,%d,%d,%d): block=%dbits key=%dbits"
                           % (self.__nRounds, self.__nRows, self.__nColumns,
                              self.__wordSize, self.__nKeyColumns,
                              self.__nColumns*self.__nRows*self.__wordSize,
                              self.__nKeyColumns*self.__nRows*self.__wordSize))
        self.__keyExpanderObj = _KeyExpansion(key, self.__nRounds,
                                              self.__nRows, self.__nColumns,
                                              self.__wordSize,
                                              self.__nKeyColumns, sboxCalc,
                                              loglevel)
        self.__subBytesObj = _SubBytes(wordSize, sboxCalc, loglevel)
        self.__shiftRowsObj = _ShiftRows(nRows, loglevel)
        self.__mixColumnsObj = _MixColumns(nRows, nColumns, wordSize, loglevel)
        self.__addRoundKeyObj = _AddRoundKey(nRows, nColumns, wordSize,
                                             loglevel)
        self.__state = None  # FIXME: this memory is not protected and shall be
        self.__round = None

    def __str__(self):
        parentesis = "%d, %d, %d, %d" % (self.__nRounds, self.__nRows,
                                         self.__nColumns, self.__wordSize)
        if self.__nKeyColumns != self.__nColumns:
            parentesis += ", %d" % (self.__nKeyColumns)
        return "Rijndael(%s)" % (parentesis)

    def __repr__(self):
        return "%s" % (self.__str__())

    # Readonly configuration ----

    @property
    def nRounds(self):
        return self.__nRounds

    @property
    def nRows(self):
        return self.__nRows

    @property
    def nColumns(self):
        return self.__nColumns

    @property
    def wordSize(self):
        return self.__wordSize

    @property
    def nKeyColumns(self):
        return self.__nKeyColumns

    @property
    def blockSize(self):
        return self.__wordSize * self.__nColumns * self.__nRows

    @property
    def keySize(self):
        return self.__wordSize * self.__nKeyColumns * self.__nRows

    @property
    def sbox(self):
        return self.__subBytesObj

    @property
    def mixColumns(self):
        return self.__mixColumnsObj

    # Interface methods ----

    def cipher(self, plain):
        '''plain (1d array) is copied to state matrix.
           After the inicial round addition, the state is transformed by the
           nRounds, finishing with the final round.
           At the end state matrix is copied to output 1d array.
           Input: <integer> plainText
           Output: <integer> cipherText
        '''
        self.__convertInput2State(plain)
        self.__round = 0
        self.__addRoundKey()  # w[0,Nb-1]
        for self.__round in range(1, self.__nRounds):  # [1..Nr-1] step 1
            self.__subBytes()
            self.__shiftRows()
            self.__mixColumns()
            self.__addRoundKey()
        self.__round = self.__nRounds
        self.__subBytes()
        self.__shiftRows()
        self.__addRoundKey()
        return self.__convertState2output()

    def decipher(self, cipher):
        '''cipher (1d array) is copied to state matrix.
           The cipher round transformations are produced in the reverse order.
           At the end state matrix is copied to the output 1d array.
           Input: <integer> cipherText
           Output: <integer> plainText
        '''
        self.__convertInput2State(cipher)
        self.__round = self.__nRounds
        self.__addRoundKey()
        # [Nr-1..1] step -1
        for self.__round in range(self.__nRounds-1, 0, -1):
            self.__invShiftRows()
            self.__invSubBytes()
            self.__addRoundKey()
            self.__invMixColumns()
        self.__round = 0
        self.__invShiftRows()
        self.__invSubBytes()
        self.__addRoundKey()
        return self.__convertState2output()

    # Rijndael Operations ----

    def __subBytes(self):
        self.__state = self.__subBytesObj.do(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "cipher->subBytes()\t")

    def __invSubBytes(self):
        self.__subBytesObj.invert(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "decipher->invSubBytes()\t")

    def __shiftRows(self):
        self.__state = self.__shiftRowsObj.do(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "cipher->shiftRows()\t")

    def __invShiftRows(self):
        self.__state = self.__shiftRowsObj.invert(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "decipher->invShiftRows()\t")

    def __mixColumns(self):
        self.__state = self.__mixColumnsObj.do(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "cipher->mixColumns()\t")

    def __invMixColumns(self):
        self.__state = self.__mixColumnsObj.invert(self.__state)
        self._debug_stream("state", self.__state, self.__round,
                           "decipher->invMixColumns()\t")

    def __addRoundKey(self):
        self.__state = self.__addRoundKeyObj.do(self.__state,
                                                self.__keyExpanderObj.getSubKey
                                                ((self.__round *
                                                  self.__nColumns),
                                                 (self.__round+1) *
                                                 (self.__nColumns)))
        self._debug_stream("state", self.__state, self.__round,
                           "cipher->addRoundKey()\t")

    # Data conversions ----

    def __convertInput2State(self, argin):
        self._debug_stream("argin: %s" % (argin))
        # TODO: check the argin have the size to be ciphered/deciphered
        anArray = _Long(self.__wordSize).toArray(argin,
                                                 self.__nColumns *
                                                 self.__nRows *
                                                 self.__wordSize)
        self.__state = _State(self.__nRows, self.__nColumns, self._logLevel).\
            fromArray(anArray)

    def __convertState2output(self):
        anArray = _State(self.__nRows, self.__nColumns,
                         self._logLevel).toArray(self.__state)
        argout = _Long(self.__wordSize).fromArray(anArray,
                                                  self.__nColumns *
                                                  self.__nRows *
                                                  self.__wordSize)
        self._debug_stream("argout: %s" % argout)
        return argout


# Test and console execution area ----


from optparse import OptionParser


def understandInteger(value):
    try:
        if value.startswith('0x'):
            return int(value, 16)
        elif value.startswith('0b'):
            return int(value, 2)
        elif value.startswith('0'):  # first check hexadecimal and binary
            return int(value, 8)
        else:
            return int(value)  # last try is to interpret as decimal
    except Exception as e:
        print("Cannot interpret %s as an integer (%e)" % (value, e))
        return None


def main():
    # TODO: introduce parameters to:
    #       - define parameters to use and use random input and key.
    #       - allow to setup by params the input and/or the key, and
    #       - operations to do: cipher and/or decipher
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    parser.add_option('', "--rounds", type="int", default=10,
                      help="Number of rounds")
    parser.add_option('', "--rows", type="int", default=4,
                      help="Number of rows")
    parser.add_option('', "--columns", type="int", default=4,
                      help="Number of columns")
    parser.add_option('', "--wordsize", type="int", default=8,
                      help="Bit size of the word")
    parser.add_option('', "--kolumns", type="int", default=4,
                      help="Number of columns of the key")
    parser.add_option('', "--key", default="0",
                      help="Key in numeric representation")
    parser.add_option('', "--plainText", default="0",
                      help="Plaintext in numeric representation")
    parser.add_option('', "--only-keyexpansion", action="store_true",
                      default=False,
                      help="No [de]cipher operations. Made to test the PRG "
                      "with the key as seed to generate each round subkeys.")
    parser.add_option('', "--calculate-sbox", default=False,
                      action="store_true",
                      help="Instead of use the given Rijndael tables, do the "
                      "polynomial calculations.")
    # TODO: add options to only [de]cipher
    #       (the will be also need a --cipherText)
    (options, args) = parser.parse_args()
    key = understandInteger(options.key)
    if key is None:
        print("\n\tError: It was not possible to understand the input key "
              "'%s' as a number.\n" % (options.key))
        sys.exit(-1)
    gr = GeneralizedRijndael(key=key,
                             nRounds=options.rounds,
                             nRows=options.rows,
                             nColumns=options.columns,
                             wordSize=options.wordsize,
                             nKeyColumns=options.kolumns,
                             sboxCalc=options.calculate_sbox,
                             loglevel=_levelFromMeaning(options.log_level))
    if not options.only_keyexpansion:
        plainText = understandInteger(options.plainText)
        if plainText is None:
            print("\n\tError: It was not possible to understand the input "
                  "plain text '%s' as a number.\n" % (options.plainText))
            sys.exit(-2)
        cipherText = gr.cipher(plainText)
        if int(plainText) != gr.decipher(cipherText):
            print("Error")
        else:
            print("Ok")
        print("Release: %s" % (version()))

if __name__ == "__main__":
    main()
