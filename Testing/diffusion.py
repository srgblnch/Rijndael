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
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

# from datetime import datetime
from gRijndael.AddRoundKey import AddRoundKey as _AddRoundKey
from gRijndael.KeyExpansion import KeyExpansion as _KeyExpansion
from gRijndael.Logger import levelFromMeaning
from gRijndael.MixColumns import MixColumns as _MixColumns
from gRijndael.SubBytes import SubBytes as _SubBytes
from gRijndael.ShiftRows import ShiftRows as _ShiftRows
from gRijndael.ThirdLevel import Long as _Long
from gRijndael.ThirdLevel import State as _State
from gRijndaelTest import extractParams
from optparse import OptionParser
from traceback import print_exc


class Convertible(object):
    def __init__(self):
        super(Convertible, self).__init__()

    def int2matrix(self, argin):
        return _State(self._nRows, self._nColumns).\
            fromArray(_Long(self._wordSize).toArray(argin, self._blockSize))

    def matrix2int(self, argin):
        return _Long(self._wordSize).\
            fromArray(_State(self._nRows, self._nColumns).toArray(argin),
                      self._blockSize)

    def int2key(self, argin):
        return _Long(self._blockSize).toArray(argin, self._blockSize)

    def key2int(self, argin):
        return _Long(self._blockSize).fromArray(argin, self._blockSize)

    def int2subkey(self, argin):
        return _Long(self._nKeyColumns*self._wordSize).\
            toArray(argin, self._blockSize)

    def subkey2int(self, argin):
        return _Long(self._nKeyColumns*self._wordSize).\
            fromArray(argin, self._blockSize)


class RindaelTest(Convertible):
    def __init__(self, logLevel, nRounds, nRows, nColumns, wordSize,
                 nKeyColumns):
        super(RindaelTest, self).__init__()
        print("nRounds = %d, nRows = %d, nColumns = %d, wordSize = %d, "
              "nKeyColumns = %d"
              % (nRounds, nRows, nColumns, wordSize, nKeyColumns))
        self._nRounds = nRounds
        self._nRows = nRows
        self._nColumns = nColumns
        self._wordSize = wordSize
        self._nKeyColumns = nKeyColumns
        self._blockSize = nRows*nColumns*wordSize
        self._keySize = nRows*nKeyColumns*wordSize
        self._key = 0
        self._keyExpansionObj = _KeyExpansion(self._key, self._nRounds, 
                                              self._nRows, self._nColumns, 
                                              self._wordSize,
                                              self._nKeyColumns,
                                              loglevel=logLevel)
        self._subBytesObj = _SubBytes(self._wordSize, loglevel=logLevel)
        self._shiftRowsObj = _ShiftRows(self._nRows, loglevel=logLevel)
        self._mixColumnsObj = _MixColumns(self._nRows, self._nColumns,
                                          self._wordSize, loglevel=logLevel)
        self._addRoundKeyObj = _AddRoundKey(self._nRows, self._nColumns,
                                            self._wordSize, loglevel=logLevel)
        self._round = 0
        self._state = self.int2matrix(0)
        self._bitFlags = 0

    def addRoundKey(self):
        subkey = self._keyExpansionObj.getSubKey(self._round*4,
                                                 (self._round+1)*4)
        self._state = self._addRoundKeyObj.do(self._state, subkey)
        stateInt = self.matrix2int(self._state)
        print stateInt
        self._bitFlags |= stateInt
        if self._bitFlags == 2**self._blockSize-1:
            raise StopIteration("Full diffusion at round %d, in addRoundKey()"
                                % (self._round))

    def subBytes(self):
        self._state = self._subBytesObj.do(self._state)
        stateInt = self.matrix2int(self._state)
        print stateInt
        self._bitFlags |= stateInt
        if self._bitFlags == 2**self._blockSize-1:
            raise StopIteration("Full diffusion at round %d, in subBytes()"
                                % (self._round))

    def shiftRows(self):
        self._state = self._shiftRowsObj.do(self._state)
        stateInt = self.matrix2int(self._state)
        print stateInt
        self._bitFlags |= stateInt
        if self._bitFlags == 2**self._blockSize-1:
            raise StopIteration("Full diffusion at round %d, in shiftRows()"
                                % (self._round))

    def mixColumns(self):
        self._state = self._mixColumnsObj.do(self._state)
        stateInt = self.matrix2int(self._state)
        print stateInt
        self._bitFlags |= stateInt
        if self._bitFlags == 2**self._blockSize-1:
            raise StopIteration("Full diffusion at round %d, in mixColumns()"
                                % (self._round))

    def encrypt(self):
        self._bitFlags = 0
        # round 0 ---
        self._round = 0
        self.addRoundKey()
        for i in range(1, self._nRounds):
            # ith round ---
            self._round = i
            self.subBytes()
            self.shiftRows()
            self.mixColumns()
            self.addRoundKey()
        # last round ---
        self._round = self._nRounds
        self.subBytes()
        self.shiftRows()
        self.addRoundKey()

    def diffusionLoop(self, operations):
        self._bitFlags = 0
        for i in range(self._nRounds+1):
            for operation in operations:
                operation()

    def subBytesDiffusion(self):
        self.diffusionLoop([self.subBytes])

    def shiftRowsDiffusion(self):
        self.diffusionLoop([self.shiftRows])

    def mixColumnsDiffusion(self):
        self.diffusionLoop([self.mixColumns])

    def subBytesAndmixColumnsDiffusion(self):
        self.diffusionLoop([self.subBytes, self.mixColumns])


def encryptionDiffusion(operation):
    try:
        operation()
    except StopIteration as e:
        print("Test succeed: %s" % e)
    except Exception as e:
        print("Something went wrong: %s" % e)
        print_exc()
    else:
        print("Test failed, no full diffusion")


def main():
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    parser.add_option('', "--rijndael", type='str',
                      help="Comma separated set of Rijndael's generalised"
                      "parameters. For example from the original Rijndael: "
                      "10,4,4,8 for 128, or 12,4,4,8,6 for 192 or "
                      "14,4,4,8,8 for 256 "
                      "(nRounds, nRows, nColumns, wordSize[, nKeyColumns])")
    import sys
    (options, args) = parser.parse_args()
    loglevel = levelFromMeaning(options.log_level)
    if options.rijndael is not None:
        parameters = extractParams(options.rijndael)
        rindaelTest = RindaelTest(options.log_level, *parameters)
        print("Encryption process")
        encryptionDiffusion(rindaelTest.encrypt)
        print("subBytes process")
        encryptionDiffusion(rindaelTest.subBytesDiffusion)
        print("shiftRows process")
        encryptionDiffusion(rindaelTest.shiftRowsDiffusion)
        print("mixColumns process")
        encryptionDiffusion(rindaelTest.mixColumnsDiffusion)
        print("subBytes & mixColumns process")
        encryptionDiffusion(rindaelTest.subBytesAndmixColumnsDiffusion)


if __name__ == "__main__":
    main()