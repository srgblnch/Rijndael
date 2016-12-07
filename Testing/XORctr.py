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

from datetime import datetime
from gRijndael.Polynomials import *
from gRijndael import SBox
from gRijndael import KeyExpansion
from gRijndael import AddRoundKey
from gRijndael import SubBytes
from gRijndael import MixColumns
from gRijndael import gRijndael
from gRijndael.Logger import levelFromMeaning
from gRijndaelTest import extractParams
from numpy import array
from optparse import OptionParser
from random import randint


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
            c_x, ring, field = \
                getPolynomialRingWithBinaryCoefficients(degree, coeffdegree)
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
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
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
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    subkey = [randint(0, 2**(wordSize*nRows))
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
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
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
    state = [[randint(0, 2**wordSize)
              for i in range(nColumns)]
             for j in range(nRows)]
    mixColumns.do(state)
    print("MixColumns(%2d, %2d, %2d)-> %6d xors"
          % (nRows, nColumns, wordSize, mixColumns.xors))


def gRijndaelXORxtr():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = "%s_gRijndaelXORxtr.csv" % (now)
    with open(fileName, 'a') as f:
        f.write("rounds\trow\tcolumns\twordsize\tkolumns\tblock\tkey"
                "\tsamples\tencrMean\tencrStd\tdecrMean\tdecrStd\n")
    errors = []
    for nRows in range(2, 9):
        for nColumns in range(2, 17):
            for wordSize in range(3, 17):
                for nKolumns in range(2, 17):
                    nRounds = max(nKolumns, nColumns) + 6
                    blockSize = nRows*nColumns*wordSize
                    keySize = nRows*nKolumns*wordSize
                    try:
                        doRijndael(fileName, nRounds, nRows, nColumns,
                                   wordSize, nKolumns)
                    except AssertionError as e:
                        print("gRijndael(%2d, %2d, %2d, %2d, %2d): "
                              "(b%4d, k%4d)-> Exception: %s"
                              % (nRounds, nRows, nColumns, wordSize, nKolumns,
                                 blockSize, keySize, e))
                        with open(fileName, 'a') as f:
                            f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d"
                                    "\t%s\t%s\t%s\t%s\n"
                                    % (nRounds, nRows, nColumns, wordSize,
                                       nKolumns, blockSize, keySize, "NaN",
                                       "NaN", "NaN", "NaN"))
                        errors.append([nRounds, nRows, nColumns, wordSize,
                                       nKolumns, e])
    if len(errors) > 0:
        print("Issues found in the process:")
        for error in errors:
            try:
                nRounds, nRows, nColumns, wordSize, nKolumns, e = error
                print("\tgRijndael(%2d, %2d, %2d, %2d, %2d): %s"
                      % (nRounds, nRows, nColumns, wordSize, nKolumns, e))
            except:
                print("\t%s" % e)


def doRijndael(fileName, nRounds, nRows, nColumns, wordSize, nKolumns):
    encrXors = []
    decrXors = []
    for i in range(nRows*nColumns):
        data = randint(0, 2**(nRows*nColumns*wordSize))
        key = randint(0, 2**(nRows*nKolumns*wordSize))
        rijndael = gRijndael(key, nRounds, nRows, nColumns, wordSize, nKolumns)
        encData = rijndael.cipher(data)
        encrXors.append(rijndael.xors)
        rijndael.reset()
        if data != rijndael.decipher(encData):
            raise AssertionError("gRijndael(%2d, %2d, %2d, %2d, %2d)"
                                 % (nRounds, nRows, nColumns, wordSize,
                                    nKolumns))
        decrXors.append(rijndael.xors)
        rijndael.reset()
#         print("gRijndael(%2d, %2d, %2d, %2d, %2d): (b%4d, k%4d)-> "
#               "%9d xors & %9d xors"
#               % (nRounds, nRows, nColumns, wordSize, nKolumns,
#                  rijndael.blockSize, rijndael.keySize, encrXors[-1],
#                  decrXors[-1]))
    encrXors = array(encrXors)
    decrXors = array(decrXors)
    print("gRijndael(%2d, %2d, %2d, %2d, %2d): (b%4d, k%4d)-> "
              "%9d xors (%10g) & %9d xors (%10g) %d samples"
              % (nRounds, nRows, nColumns, wordSize, nKolumns,
                 rijndael.blockSize, rijndael.keySize, encrXors.mean(),
                   encrXors.std(), decrXors.mean(), decrXors.std(),
                   nRows*nColumns))
    with open(fileName, 'a') as f:
        f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%e\t%d\t%e\n"
                % (nRounds, nRows, nColumns, wordSize, nKolumns,
                   rijndael.blockSize, rijndael.keySize, nRows*nColumns,
                   encrXors.mean(), encrXors.std(),
                   decrXors.mean(), decrXors.std()))


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
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = "%s_gRijndaelXORxtr.csv" % (now)
        doRijndael(fileName, *parameters)
    else:
        # BinaryPolynomialsXORCtr()
        # PolynomialRingXORCtr()
        # SBoxXORctr()
        # keyExpansionXORctr()
        # addRoundKeyXORctr()
        # subBytesXORctr()
        # mixColumnsXORctr()
        gRijndaelXORxtr()


if __name__ == "__main__":
    main()
