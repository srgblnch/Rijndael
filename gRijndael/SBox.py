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

from copy import deepcopy as _deepcopy
from .Logger import Logger as _Logger
from .Logger import XORctr as _XORctr
from .Polynomials import getBinaryExtensionFieldModulo
from .Polynomials import getBinaryExtensionRingModulo
from .Polynomials import getMu, getNu
from .Polynomials import BinaryExtensionModulo


class SBox(_Logger, _XORctr):
    '''This class is used from the subBytes rijndael's transformation. But it
       is using an auxiliar python source file who have stored the original
       sbox and its inverse, for 8 bits word size, as well as it have two
       other pairs of sboxes for word size 2 and 4 made on this development.
    '''
    def __init__(self, wordSize,
                 # useCalc=True,
                 *args, **kwargs):
        super(SBox, self).__init__(*args, **kwargs)
        # TODO: this must be able to be modified to use a sbox as a table ----
        #       or as the pure calculations
        self._useCalc = True  # useCalc
        self.__wordSize = wordSize
        if self._useCalc:
            field_modulo = getBinaryExtensionFieldModulo(wordSize)
            self._field = BinaryExtensionModulo(field_modulo)
            ring_modulo = getBinaryExtensionRingModulo(wordSize)
            self._ring = BinaryExtensionModulo(ring_modulo)
#         else:
#             if wordSize == 8:
#                 self._sbox = sbox_word8b
#                 self._sbox_inverted = sbox_word8b_inverted
# #            elif  self.__wordSize == 4:
# #                self._sbox = sbox_word4b
# #                self._sbox_inverted = sbox_word4b_inverted
# #            elif  self.__wordSize == 2:
# #                self._sbox = sbox_word2b
# #                self._sbox_inverted = sbox_word2b_inverted
#             if not (hasattr(self, "_sbox") or \
#                     hasattr(self, "_sbox_inverted")):
#                 raise Exception("(__init__)",
#                                 "There is no Sbox for %d wordsize"
#                                 % (self.__wordSize))

    def getField(self):
        if self._useCalc:
            return self._field
        else:
            return "z^8+z^4+z^3+z+1 (the Rijndael's original)"

    def getRing(self):
        if self._useCalc:
            return self._ring
        else:
            return "z^8+1 (the Rijndael's original)"

    def getMu(self):
        if self._useCalc:
            return self._ring(getMu(self.__wordSize))
        else:
            return "z^4+z^3+z^2+z+1 (the Rijndael's original)"

    def getNu(self):
        if self._useCalc:
            return self._ring(getNu(self.__wordSize))
        else:
            return "z^6+z^5+z+1 (the Rijndael's original)"

    def transform(self, state, invert=False):
        '''Given the content of one cell of the state matrix, 'divide' in 2
           halfs. The upper is understood as the row and the lower as the
           column in the sbox. The sbox is a paramenter because the
           transformation use one sbox or its invers, but the procedure is
           the same.
           Input:
           Output:
        '''
        output = _deepcopy(state)
        if self._useCalc:
            if invert:
                sbox = self._invertsbox_call_
            else:
                sbox = self._sbox_call_
            for i in range(len(output)):
                if type(output[i]) == list:
                    for j in range(len(output[i])):
                        output[i][j] = sbox(output[i][j])
                else:
                    output[i] = sbox(output[i])
#         else:
#             if invert:
#                 sbox = self._sbox_inverted
#             else:
#                 sbox = self._sbox
#             for i in range(len(output)):
#                 if type(output[i]) == list:
#                     for j in range(len(output[i])):
#                         r, c = self.__hexValue2MatrixCoords(output[i][j])
#                         output[i][j] = sbox[r][c]
#                 else:
#                     r, c = self.__hexValue2MatrixCoords(output[i])
#                     output[i] = sbox[r][c]
        return output

#     def __hexValue2MatrixCoords(self, value):
#         '''Split the input in to equal halfs that will be used as coordinates
#            in the sbox transformations.
#            Input: <integer> value
#            Output: <integer> row, <integer> column
#         '''
#         if self.__wordSize % 2 == 1:
#             raise Exception("(__hexValue2MatrixCoords)", "Matrix "
#                             "coordinates impossible for an odd %d wordsize"
#                             % (self.__wordSize))
#         cmask = '0b'+'1'*(self.__wordSize/2)
#         rmask = '0b'+'1'*(self.__wordSize/2)+'0'*(self.__wordSize/2)
#         c = (value & int(cmask, 2))
#         r = (value & int(rmask, 2)) >> (self.__wordSize/2)
#         return r, c

    def _sbox_call_(self, value):
        g = ~self._field(value)
        self._debug_stream("%s -> %s" % (value, g), operation="SBox")
        ax = self._ring(g._coefficients)
        self._debug_stream("%s -> %s" % (value, ax), operation="SBox")
        mu = self.getMu()
        nu = self.getNu()
        bx = (mu * ax) + nu  # bx = (mu.__matrix_product__(ax))+nu
        self._debug_stream("b(z) = mu(z) * a(z) + nu(z) = %s * %s + %s = %s"
                           % (mu, ax, nu, bx), operation="SBox")
        self._debug_stream("SBox(%s) -> %s" % (value, bx.coefficients),
                           operation="SBox")
        self.xors = bx.xors + g.xors
        return bx._coefficients

    def _invertsbox_call_(self, value):
        bx = self._ring(value)
        self._debug_stream("%s -> %s" % (value, bx), operation="SBox")
        inv_mu = ~self.getMu()
        nu = self.getNu()
        ax = (inv_mu * (bx-nu))  # ax = inv_mu.__matrix_product__(bx-nu)
        element = ~self._field(ax._coefficients)
        self._debug_stream("a(z) = ~mu(z) * b(z) + nu(z) = %s * %s + %s = %s"
                           % (inv_mu, bx, nu, ax), operation="SBox")
        self._debug_stream("SBox(%s) -> %s" % (value, element.coefficients),
                           operation="~SBox")
        self.xors = element.xors + inv_mu.xors
        return element._coefficients

# # the sbox, with wordsize = 8
# # 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
# # 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
# sbox_word8b = \
#     [[0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,
#       0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76],  # 0x0
#      [0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0,
#       0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0],  # 0x1
#      [0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC,
#       0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15],  # 0x2
#      [0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A,
#       0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75],  # 0x3
#      [0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0,
#       0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84],  # 0x4
#      [0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B,
#       0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF],  # 0x5
#      [0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85,
#       0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8],  # 0x6
#      [0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5,
#       0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2],  # 0x7
#      [0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17,
#       0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73],  # 0x8
#      [0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88,
#       0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB],  # 0x9
#      [0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C,
#       0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79],  # 0xA
#      [0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9,
#       0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08],  # 0xB
#      [0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6,
#       0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A],  # 0xC
#      [0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E,
#       0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E],  # 0xD
#      [0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94,
#       0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF],  # 0xE
#      [0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68,
#       0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16]   # 0xF
#      ]

# # 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
# # 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
# sbox_word8b_inverted = \
#     [[0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38,
#       0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB],  # 0x0
#      [0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87,
#       0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB],  # 0x1
#      [0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D,
#       0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E],  # 0x2
#      [0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2,
#       0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25],  # 0x3
#      [0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16,
#       0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92],  # 0x4
#      [0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA,
#       0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84],  # 0x5
#      [0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A,
#       0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06],  # 0x6
#      [0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02,
#       0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B],  # 0x7
#      [0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA,
#       0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73],  # 0x8
#      [0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85,
#       0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E],  # 0x9
#      [0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89,
#       0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B],  # 0xA
#      [0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20,
#       0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4],  # 0xB
#      [0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31,
#       0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F],  # 0xC
#      [0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D,
#       0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF],  # 0xD
#      [0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0,
#       0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61],  # 0xE
#      [0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26,
#       0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D]   # 0xF
#      ]

# FIXME:!!! Alert, this sboxes are not build correctly !!!

# #FIXME: 0b0011
# sbox_word4b = [#the sbox, with wordsize = 4
# # 0b00, 0b01, 0b10, 0b11,
# [0b0110,0b1011,0b0101,0b0100],#0b00
# [0b0010,0b1110,0b0111,0b1010],#0b01
# [0b1001,0b1101,0b1111,0b1100],#0b10
# [0b0011,0b0001,0b0000,0b1000],#0b11
# ]
#
# sbox_word4b_inverted = [
# # 0b00, 0b01, 0b10, 0b11,
# [0b1011,0b1100,0b1111,0b1110],#0b00
# [0b0111,0b1000,0b0010,0b0110],#0b01
# [0b0001,0b0000,0b1101,0b0101],#0b10
# [0b0011,0b1001,0b0100,0b1010],#0b11
# ]
#
# sbox_word2b = [#the sbox, with wordsize = 2
# # 0b0, 0b1
# [0b01,0b00],#0b0
# [0b11,0b10],#0b1
# ]
#
# sbox_word2b_inverted = [
# # 0b0, 0b1
# [0b10,0b11],#0b0
# [0b00,0b01],#0b1
# ]


def main():
    '''Test the correct functionality of SBox transformations.
    '''
    wordSize = 8
    loglevel = Logger._debug

    # SBoxUsingTables = SBox(wordSize, loglevel=loglevel)
    SBoxUsingCalculation = SBox(wordSize, loglevel=loglevel)  # , useCalc=True)

    # TODO: loop with a bigger sample set.
    bar = 0
    # barUsingTables = SBoxUsingTables.transform([bar])[0]
    barUsingCalculation = SBoxUsingCalculation.transform([bar])[0]

#     if barUsingTables != barUsingCalculation:
#         print("\n\tError: test not passed!\n\tFrom %d, using tables we get "
#               "'%s' and using calculation has been '%s'\n"
#               % (bar, barUsingTables, barUsingCalculation))
    # TODO: check the inverse transformation.


if __name__ == "__main__":
    main()
