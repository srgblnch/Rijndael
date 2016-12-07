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

# From AES Proposal: Rijndael v2 1999/09/03
# section 7.6
#    Two rounds of Rijndael provide "full diffusion" in the following sense:
# every state bit depends on all state bits two rounds ago, or, a change in
# one state bit is likely to affect half of the state bits after two rounds.
# Adding 4 rounds can be seen as adding a "full diffusion" step at the
# beginning and at the end of the cipher. The high diffusion of a Rijndael
# round is thanks to its uniform structure that operates on all state bits.
# For so-called Feistel ciphers, a round only operates on half of the state
# bits and full diffusion can at best be obtained after 3 rounds and in
# practice it typically takes 4 rounds or more.

# Then, having two state matrix with one single bit different (all 0s in one,
# and the other identical but with one single 1 somewhere), how many rounds
# are necessary to have at least half different state bits. That is, the
# hamming distance between two vectors.


from datetime import datetime
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

    def hammingWeight(self, value):
        """Get the hamming weight of the polynomial.
           Hamming weight is defined as the number of non null elements. In
           the binary case, the number of ones.
        """
        return bin(value).count('1')


class DiffusionTest(Convertible):
    def __init__(self, logLevel, nRounds, nRows, nColumns, wordSize,
                 nKeyColumns):
        super(DiffusionTest, self).__init__()
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
        self.resetStates()

    def resetStates(self):
        self._round = 0
        self._stateA = self.int2matrix(0)
#         self._stateB = self._stateA[:]
#         rbit = (randint(0, self._nRows-1), randint(0, self._nColumns-1),
#                 randint(0, self.__wordSize))
        self._stateB = self.int2matrix(1)

    def addRoundKey(self):
        subkey = \
            self._keyExpansionObj.getSubKey(self._round*self._nColumns,
                                            (self._round+1)*self._nColumns)
        self._stateA = self._addRoundKeyObj.do(self._stateA, subkey)
        self._stateB = self._addRoundKeyObj.do(self._stateB, subkey)
        stateDist = self.diffStates()
#         print("Round %d, addRoundKey() diffusion: %d"
#               % (self._round, stateDist))
        if stateDist > self._blockSize/2:
            raise StopIteration([self._round,
                                 "Reached half-diffusion (%d) with %d rounds "
                                 "with addRoundKey() operation"
                                 % (stateDist, self._round)])

    def subBytes(self):
        self._stateA = self._subBytesObj.do(self._stateA)
        self._stateB = self._subBytesObj.do(self._stateB)
        stateDist = self.diffStates()
#         print("Round %d, subBytes() diffusion: %d"
#               % (self._round, stateDist))
        if stateDist > self._blockSize/2:
            raise StopIteration([self._round,
                                 "Reached half-diffusion (%d) with %d rounds "
                                 "with subBytes() operation"
                                 % (stateDist, self._round)])

    def shiftRows(self):
        self._stateA = self._shiftRowsObj.do(self._stateA)
        self._stateB = self._shiftRowsObj.do(self._stateB)
        stateDist = self.diffStates()
#         print("Round %d, shiftRows() diffusion: %d"
#               % (self._round, stateDist))
        if stateDist > self._blockSize/2:
            raise StopIteration([self._round,
                                 "Reached half-diffusion (%d) with %d rounds "
                                 "with shiftRows() operation"
                                 % (stateDist, self._round)])

    def mixColumns(self):
        self._stateA = self._mixColumnsObj.do(self._stateA)
        self._stateB = self._mixColumnsObj.do(self._stateB)
        stateDist = self.diffStates()
#         print("Round %d, mixColumns() diffusion: %d"
#               % (self._round, stateDist))
        if stateDist > self._blockSize/2:
            raise StopIteration([self._round,
                                 "Reached half-diffusion (%d) with %d rounds "
                                 "with mixColumns() operation"
                                 % (stateDist, self._round)])

    def diffStates(self):
        diff = self.matrix2int(self._stateA) ^ self.matrix2int(self._stateB)
        return self.hammingWeight(diff)

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
        self.resetStates()
        for self._round in range(self._nRounds+1):
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
        print("Test succeed: %s" % e.message[1])
        return e.message[0]
    except Exception as e:
        print("Something went wrong: %s" % e)
        print_exc()
    else:
        print("Test failed, no full diffusion")
    return -1


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
        rindaelTest = DiffusionTest(options.log_level, *parameters)
        print("Encryption process")
        halfdiffusion = encryptionDiffusion(rindaelTest.encrypt)
        print("\n\tHalf-diffusion: %d" % (halfdiffusion))
        print("\tFull-diffusion: %d\n\n" % (halfdiffusion*2))
#         print("subBytes process")
#         if encryptionDiffusion(rindaelTest.subBytesDiffusion):
#             print("\n\tFull diffusion: %d\n\n" % (halfdiffusion*2))
#         print("shiftRows process")
#         if encryptionDiffusion(rindaelTest.shiftRowsDiffusion):
#             print("\n\tFull diffusion: %d\n\n" % (halfdiffusion*2))
#         print("mixColumns process")
#         if encryptionDiffusion(rindaelTest.mixColumnsDiffusion):
#             print("\n\tFull diffusion: %d\n\n" % (halfdiffusion*2))
#         print("subBytes & mixColumns process")
#         if encryptionDiffusion(rindaelTest.subBytesAndmixColumnsDiffusion):
#             print("\n\tFull diffusion: %d\n\n" % (halfdiffusion*2))
    else:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = "%s_fulldiffusion.csv" % (now)
        with open(fileName, 'a') as f:
            f.write("rounds\trow\tcolumns\twordsize\tkolumns\tblock\tkey"
                    "\tfull-diffusion\n")
        for nRows in range(2, 9):
            for nColumns in range(2, 17):
                for wordSize in range(3, 17):
                    for nKolumns in range(2, 17):
                        if nKolumns >= nColumns:
                            nRounds = max(nKolumns, nColumns) + 6
                            blockSize = nRows*nColumns*wordSize
                            keySize = nRows*nKolumns*wordSize
                            rindaelTest = DiffusionTest(options.log_level,
                                                        nRounds, nRows,
                                                        nColumns, wordSize,
                                                        nKolumns)
                            halfdiffusion = \
                                encryptionDiffusion(rindaelTest.encrypt)
                            print("nRounds = %2d, nRows = %2d, "
                                  "nColumns = %2d, wordSize = %2d, "
                                  "nKeyColumns = %2d, blockSize = %4d, "
                                  "keySize = %4s -> full-diffusion = %2d"
                                  % (nRounds, nRows, nColumns, wordSize,
                                     nKolumns, blockSize, keySize,
                                     halfdiffusion*2))
                            with open(fileName, 'a') as f:
                                f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"
                                        % (nRounds, nRows, nColumns, wordSize,
                                           nKolumns, blockSize, keySize,
                                           halfdiffusion*2))

if __name__ == "__main__":
    main()
