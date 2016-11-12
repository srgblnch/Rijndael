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

from gRijndael.Polynomials import *
from random import randint
from gRijndael import SBox
from gRijndael import KeyExpansion
from gRijndael import AddRoundKey
from gRijndael import SubBytes
from gRijndael import MixColumns
from gRijndael import gRijndael


def BinaryPolynomialsXORCtr():
    for degree in range(2, 17):
        for field in [False, True]:
            if field:
                msg = "%2d degree binary extension field" % (degree)
                getModulo = getBinaryExtensionFieldModulo
            else:
                msg = "%2d degree binary extension ring " % (degree)
                getModulo = getBinaryExtensionRingModulo
            modulo = BinaryExtensionModulo(getModulo(degree))
            zero = modulo(0)
            one = modulo(1)
            biggest = modulo(2**degree-1)
            sample = modulo(randint(0, 2**degree))
            sample += zero
            sample += one
            sample += biggest
            sample *= zero
            sample *= one
            sample *= biggest
            print("%s: 3 additions and 3 products -> %4d xors"
                  % (msg, sample.xors))


def PolynomialRingXORCtr():
    for degree in range(2, 9):
        for coeffdegree in range(2, 17):
            c_x, ring, field = getPolynomialRingWithBinaryCoefficients\
                (degree, coeffdegree)
            c_x += c_x
            c_x += c_x
            c_x += c_x
            c_x *= c_x
            c_x *= c_x
            c_x *= c_x
            print("%2d ring degree with %2d coefficients degree: "
                  "3 additions and 3 products -> %4d xors"
                  % (degree, coeffdegree, c_x.xors))


def SBoxXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                doSBox(nRows, nColumns, wordSize)


def doSBox(nRows, nColumns, wordSize):
    sbox = SBox(wordSize)
#     state = [[2**wordSize  # randint(0, 2**wordSize)\
#               for i in range(nRows)]\
#              for j in range(nColumns)]
    state = [[randint(0, 2**wordSize)\
              for i in range(nColumns)]\
             for j in range(nRows)]
    sbox.transform(state)
    print("%2d x %2d matrix with %2d bits cell: SBox transformation -> "
          "%5d xors" % (nRows, nColumns, wordSize, sbox.xors))


def keyExpansionXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 17):
            for wordSize in range(3, 17):
                for nKolumns in range(2, 17):
                    nRounds = max(nKolumns, nColumns) + 6
                    doKeyExpansion(nRounds, nRows, nColumns, wordSize,
                                   nKolumns)
     
def doKeyExpansion(nRounds, nRows, nColumns, wordSize, nKeyWords):
    keyExp = KeyExpansion(0, nRounds, nRows, nColumns, wordSize, nKeyWords)
    keyExp.getKey()
    print("KeyExpansion(%2d, %2d, %2d, %2d, %2d)-> %6d xors"
          % (nRounds, nRows, nColumns, wordSize, nKeyWords, keyExp.xors))


def addRoundKeyXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                doAddRoundKey(nRows, nColumns, wordSize)


def doAddRoundKey(nRows, nColumns, wordSize):
    ark = AddRoundKey(nRows, nColumns, wordSize)
    state = [[randint(0, 2**wordSize)\
              for i in range(nColumns)]\
             for j in range(nRows)]
    subkey = [randint(0, 2**(wordSize*nRows))\
             for j in range(nColumns)]
    ark.do(state, subkey)
    print("addRoundKey(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, ark.xors))


def subBytesXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                    doSubBytes(nRows, nColumns, wordSize)


def doSubBytes(nRows, nColumns, wordSize):
    subBytes = SubBytes(wordSize)
    state = [[randint(0, 2**wordSize)\
              for i in range(nColumns)]\
             for j in range(nRows)]
    subBytes.do(state)
    print("subBytes(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, subBytes.xors))


# ShiftRows doesn't do any xor operation


def mixColumnsXORctr():
    for nRows in range(2, 9):
        for nColumns in range(2, 9):
            for wordSize in range(3, 17):
                    doMixColumns(nRows, nColumns, wordSize)


def doMixColumns(nRows, nColumns, wordSize):
    mixColumns = MixColumns(nRows, nColumns, wordSize)
    state = [[randint(0, 2**wordSize)\
              for i in range(nColumns)]\
             for j in range(nRows)]
    mixColumns.do(state)
    print("MixColumns(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, mixColumns.xors))


def gRijndaelXORxtr():
    for nRows in range(2, 9):
        for nColumns in range(2, 17):
            for wordSize in range(3, 17):
                for nKolumns in range(2, 17):
                    nRounds = max(nKolumns, nColumns) + 6
                    doRijndael(nRounds, nRows, nColumns, wordSize, nKolumns)


def doRijndael(nRounds, nRows, nColumns, wordSize, nKolumns):
    data= randint(0, 2**(nRows*nColumns*wordSize))
    key = randint(0, 2**(nRows*nKolumns*wordSize))
    rijndael = gRijndael(key, nRounds, nRows, nColumns, wordSize, nKolumns)
    encData = rijndael.cipher(data)
    encrXors = rijndael.xors
    rijndael.reset()
    if data != rijndael.decipher(encData):
#         raise AssertionError("gRijndael(%2d, %2d, %2d, %2d, %2d)"
#                              % (nRounds, nRows, nColumns, wordSize, nKolumns))
        error = "AssertionError"
    else:
        error = ""
    print("gRijndael(%2d, %2d, %2d, %2d, %2d): (b%4d, k%4d)-> %7d xors & %7d xors\t%s"
          % (nRounds, nRows, nColumns, wordSize, nKolumns, rijndael.blockSize,
             rijndael.keySize, encrXors, rijndael.xors, error))


def main():
    #BinaryPolynomialsXORCtr()
    #PolynomialRingXORCtr()
    #SBoxXORctr()
    #keyExpansionXORctr()
    #addRoundKeyXORctr()
    #subBytesXORctr()
    #mixColumnsXORctr()
    gRijndaelXORxtr()


if __name__ == "__main__":
    main()
