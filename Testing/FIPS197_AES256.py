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

"""
    This file executes a test of the vectors provided by the fips-197
    for the AES256.
"""

from _FIPS197_AES256 import *
from gRijndael import gRijndael
from gRijndael.AddRoundKey import AddRoundKey as _AddRoundKey
from gRijndael.KeyExpansion import KeyExpansion as _KeyExpansion
from gRijndael.MixColumns import MixColumns as _MixColumns
from gRijndael.SubBytes import SubBytes as _SubBytes
from gRijndael.ShiftRows import ShiftRows as _ShiftRows
from gRijndael.ThirdLevel import Long as _Long
from gRijndael.ThirdLevel import State as _State
import sys
from traceback import print_exc


from gRijndael.Logger import Logger as _Logger
from gRijndael.Logger import _SILENCE
from gRijndael.Logger import _ERROR
from gRijndael.Logger import _WARNING
from gRijndael.Logger import _INFO
from gRijndael.Logger import _DEBUG
from gRijndael.Logger import _TRACE


def int2matrix(argin):
    return _State(4, 4).fromArray(_Long(8).toArray(argin, 4*4*8))


def matrix2int(argin):
    return _Long(8).fromArray(_State(4, 4).toArray(argin), 4*4*8)


def int2key(argin):
    return _Long(8).toArray(argin, 4*8*8)


def key2int(argin):
    return _Long(8).fromArray(argin, 4*8*8)


def int2subkey(argin):
    return _Long(4*8).toArray(argin, 4*4*8)


def subkey2int(argin):
    return _Long(4*8).fromArray(argin, 4*4*8)


def hexlist(argin):
    return ["%s" % hex(each) for each in argin]


class AES256:
    def __init__(self):
        key = aes256['key']
        if key != key2int(int2key(key)):
            raise AssertionError("Failed AES256: key2int")
        self._keyExpansionObj = _KeyExpansion(key, 14, 4, 4, 8, nKeyWords=8)
        self._subBytesObj = _SubBytes(8)  # , sboxCalc=False)
        self._shiftRowsObj = _ShiftRows(4)
        self._mixColumnsObj = _MixColumns(4, 4, 8)
        self._addRoundKeyObj = _AddRoundKey(4, 4, 8)
        input = aes256_round[0]['start']
        self._state = int2matrix(input)
        self._round = 0
        self._Errors = []

    def addRoundKey(self):
        subkey = self._keyExpansionObj.getSubKey(self._round*4,
                                                 (self._round+1)*4)
        if subkey != int2subkey(aes256_round[self._round]['k_sch']):
            k_sch = int2subkey(aes256_round[self._round]['k_sch'])
            self._Errors.append("Failed AES256: round%d, getSubKey()"
                                "\n\t\t\t%s\n\t\t\t%s"
                                % (self._round, hexlist(subkey),
                                   hexlist(k_sch)))
            subkey = int2subkey(aes256_round[self._round]['k_sch'])
        self._state = self._addRoundKeyObj.do(self._state, subkey)
        if matrix2int(self._state) != aes256_round[self._round]['end']:
            self._Errors.append("Failed AES256: round%d, addRoundKey()"
                                % (self._round))
            self._state = int2matrix(aes256_round[self._round]['end'])

    def subBytes(self):
        self._state = self._subBytesObj.do(self._state)
        if matrix2int(self._state) != aes256_round[self._round]['s_box']:
            self._Errors.append("Failed AES256: round%d, subBytes()"
                                % (self._round))
            self._state = int2matrix(aes256_round[self._round]['s_box'])

    def shiftRows(self):
        self._state = self._shiftRowsObj.do(self._state)
        if matrix2int(self._state) != aes256_round[self._round]['s_row']:
            self._Errors.append("Failed AES256: round%d, shiftRows()"
                                % (self._round))
            self._state = int2matrix(aes256_round[self._round]['s_row'])

    def mixColumns(self):
        self._state = self._mixColumnsObj.do(self._state)
        if matrix2int(self._state) != aes256_round[self._round]['m_col']:
            self._Errors.append("Failed AES256: round%d, mixColumns()"
                                % (self._round))
            self._state = int2matrix(aes256_round[self._round]['m_col'])

    def test(self):
        # round 0 ---
        self._round = 0
        self.addRoundKey()
        for i in range(1, 14):
            # ith round ---
            self._round = i
            self.subBytes()
            self.shiftRows()
            self.mixColumns()
            self.addRoundKey()
        # last round ---
        self._round = 14
        self.subBytes()
        self.shiftRows()
        self.addRoundKey()
        if len(self._Errors) > 0:
            raise AssertionError(self._Errors)
    #     # Finally, test the Rijndael object ---
    #     rijndaelObj = gRijndael(aes256['key'])
    #     if rijndaelObj.cipher(aes256['input']) != aes256['output']:
    #         raise AssertionError("Failed AES256: output doesn't correspond")


def main():
    try:
        test = AES256()
        test.test()
    except Exception as e:
        print("\n\tTest failed:")
        if type(e.message) == list:
            for error in e.message:
                print("\t\t%s" % error)
        else:
            print("\t\t%s" % e)
        print("\n")
        sys.exit(-1)
    else:
        print("\tAll has passed\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
