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

'''This file has been made to have cleaner code in the polynomials file, and
   concentrate every thing related with development and testing apart.
'''

from GeneralizedRijndael.Logger import levelFromMeaning as _levelFromMeaning
from GeneralizedRijndael.Polynomials import *

# ## Begin testing area ----

# # Test degree 8 polynomial field and ring ----


def testBinaryPolynomial(value, field=True):
    '''Test a value, interpreted as binary polynomial in a field or ring of
       degree 8.
    '''
    degree = 8
    if field:
        getModulo = getBinaryExtensionFieldModulo
    else:
        getModulo = getBinaryExtensionRingModulo
    modulo = BinaryExtensionModulo(getModulo(degree), loglevel=logs)
    sample = modulo(value)
    zero = modulo(0)
    print("\nTesting: %s = %s (%s) as polynomial %r"
          % (value, hex(value), bin(value), sample))
    product = sample*sample
    print("\t(%27s)^2 =\t(%27s) = %s = %s " % (sample, product,
                                               bin(product._coefficients),
                                               hex(product._coefficients)))
    i = 3
    while product != sample:  # i <= degree*52:
        product = sample * product
        print("\t(%27s)^%d =\t(%27s) = %s = %s "
              % (sample, i, product, bin(product._coefficients),
                 hex(product._coefficients)))
        if i == 2**degree:
            print("\tat %d break!" % (i))
            break
        if product == zero:
            print("\tat %d it decays to zero!" % (i))
            break
        i += 1
    print("\n")
    i = 1
    product = sample
    xtime = sample + modulo(1)
    while (i <= 1 and i > 2**degree) or xtime != sample:  # i <= degree*10:
        xtime = product.xtimes()
        print("\t%2d xtime(%27s) =\t(%27s) = %s = %s "
              % (i, product, xtime, bin(xtime._coefficients),
                 hex(xtime._coefficients)))
        product = xtime
        if i == 2**degree:
            print("\tat %d break!" % (i))
            break
        if product == zero:
            print("\tat %d it decays to zero!" % (i))
            break
        i += 1
    print("\n")
    try:
        inverse = ~sample
        print("\t(%27s)^-1 =\t(%27s) = %s = %s "
              % (sample, inverse, bin(inverse._coefficients),
                 hex(inverse._coefficients)))
        resample = ~inverse
        print("\t(%27s)^-1 =\t(%27s) = %s = %s "
              % (inverse, resample, bin(resample._coefficients),
                 hex(resample._coefficients)))
    except Exception as e:
        print("\t%s" % (e))
    print("\n")


# # Test the table C5 ----


def getBinaryPolinomialFieldInverse(value):
    '''From the table C.5 of the 'Design of Rijndael' book.
       For testing purposes.
    '''
    # 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
    # 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
    table_C5 = [[0x00, 0x01, 0x8D, 0xF6, 0xCB, 0x52, 0x7B, 0xD1,
                 0xE8, 0x4F, 0x29, 0xC0, 0xB0, 0xE1, 0xE5, 0xC7],  # 0x0
                [0x74, 0xB4, 0xAA, 0x4B, 0x99, 0x2B, 0x60, 0x5F,
                 0x58, 0x3F, 0xFD, 0xCC, 0xFF, 0x40, 0xEE, 0xB2],  # 0x1
                [0x3A, 0x6E, 0x5A, 0xF1, 0x55, 0x4D, 0xA8, 0xC9,
                 0xC1, 0x0A, 0x98, 0x15, 0x30, 0x44, 0xA2, 0xC2],  # 0x2
                [0x2C, 0x45, 0x92, 0x6C, 0xF3, 0x39, 0x66, 0x42,
                 0xF2, 0x35, 0x20, 0x6F, 0x77, 0xBB, 0x59, 0x19],  # 0x3
                [0x1D, 0xFE, 0x37, 0x67, 0x2D, 0x31, 0xF5, 0x69,
                 0xA7, 0x64, 0xAB, 0x13, 0x54, 0x25, 0xE9, 0x09],  # 0x4
                [0xED, 0x5C, 0x05, 0xCA, 0x4C, 0x24, 0x87, 0xBF,
                 0x18, 0x3E, 0x22, 0xF0, 0x51, 0xEC, 0x61, 0x17],  # 0x5
                [0x16, 0x5E, 0xAF, 0xD3, 0x49, 0xA6, 0x36, 0x43,
                 0xF4, 0x47, 0x91, 0xDF, 0x33, 0x93, 0x21, 0x3B],  # 0x6
                [0x79, 0xB7, 0x97, 0x85, 0x10, 0xB5, 0xBA, 0x3C,
                 0xB6, 0x70, 0xD0, 0x06, 0xA1, 0xFA, 0x81, 0x82],  # 0x7
                [0x83, 0x7E, 0x7F, 0x80, 0x96, 0x73, 0xBE, 0x56,
                 0x9B, 0x9E, 0x95, 0xD9, 0xF7, 0x02, 0xB9, 0xA4],  # 0x8
                [0xDE, 0x6A, 0x32, 0x6D, 0xD8, 0x8A, 0x84, 0x72,
                 0x2A, 0x14, 0x9F, 0x88, 0xF9, 0xDC, 0x89, 0x9A],  # 0x9
                [0xFB, 0x7C, 0x2E, 0xC3, 0x8F, 0xB8, 0x65, 0x48,
                 0x26, 0xC8, 0x12, 0x4A, 0xCE, 0xE7, 0xD2, 0x62],  # 0xA
                [0x0C, 0xE0, 0x1F, 0xEF, 0x11, 0x75, 0x78, 0x71,
                 0xA5, 0x8E, 0x76, 0x3D, 0xBD, 0xBC, 0x86, 0x57],  # 0xB
                [0x0B, 0x28, 0x2F, 0xA3, 0xDA, 0xD4, 0xE4, 0x0F,
                 0xA9, 0x27, 0x53, 0x04, 0x1B, 0xFC, 0xAC, 0xE6],  # 0xC
                [0x7A, 0x07, 0xAE, 0x63, 0xC5, 0xDB, 0xE2, 0xEA,
                 0x94, 0x8B, 0xC4, 0xD5, 0x9D, 0xF8, 0x90, 0x6B],  # 0xD
                [0xB1, 0x0D, 0xD6, 0xEB, 0xC6, 0x0E, 0xCF, 0xAD,
                 0x08, 0x4E, 0xD7, 0xE3, 0x5D, 0x50, 0x1E, 0xB3],  # 0xE
                [0x5B, 0x23, 0x38, 0x34, 0x68, 0x46, 0x03, 0x8C,
                 0xDD, 0x9C, 0x7D, 0xA0, 0xCD, 0x1A, 0x41, 0x1C],  # 0xF
                ]
    c = value & 0x0f
    r = (value & 0xf0) >> 4
    return table_C5[r][c]


def testTableC5():
    degree = 8
    field = BinaryExtensionModulo(getBinaryExtensionFieldModulo(degree),
                                  loglevel=logs)
    ok, failed = 0, 0
    for i in range(256):
        p = field(i)
        calc = ~p
        table = getBinaryPolinomialFieldInverse(i)
        if calc._coefficients != table:
            print("Alert for %4s (%27s):\ttable say %4s (%27s) and "
                  "calculation %5s (%27r)"
                  % (hex(i), field(i), hex(table), field(table), hex(calc),
                     calc))
            failed += 1
        else:
            if p.isZero or p * calc == field(1):
                ok += 1
            else:
                print("Alert %s * %s != %r" % (p, calc, field(1)))
    return (ok, failed)


def testC5():
    ok, failed = testTableC5()
    msg = "%d ok %s" % (ok, "but failed %s" % (failed) if failed > 0 else "")
    print("Check with the Rijndael's table c5: %s\n" % (msg))


def testPolynomialInverse(degree):
    field = BinaryExtensionModulo(getBinaryExtensionFieldModulo(degree),
                                  loglevel=logs)
    ok, failed = 0, 0
    for i in range(2**degree):
        p = field(i)
        calc = ~p
        if p.isZero or p * calc == field(1):
            ok += 1
        else:
            print("Alert %s * %s != %r" % (p, calc, field(1)))
    return (ok, failed)


def getRijndaelsAffineMapping(value, inverse=False):
    '''From the table C.3 and its invers C.4 of the 'Design of Rijndael' book.
       For testing purposes.
    '''
    # 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
    # 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
    table_C3 = [[0x63, 0x7C, 0x5D, 0x42, 0x1F, 0x00, 0x21, 0x3E,
                 0x9B, 0x84, 0xA5, 0xBA, 0xE7, 0xF8, 0xD9, 0xC6],  # 0x0
                [0x92, 0x8D, 0xAC, 0xB3, 0xEE, 0xF1, 0xD0, 0xCF,
                 0x6A, 0x75, 0x54, 0x4B, 0x16, 0x09, 0x28, 0x37],  # 0x1
                [0x80, 0x9F, 0xBE, 0xA1, 0xFC, 0xE3, 0xC2, 0xDD,
                 0x78, 0x67, 0x46, 0x59, 0x04, 0x1B, 0x3A, 0x25],  # 0x2
                [0x71, 0x6E, 0x4F, 0x50, 0x0D, 0x12, 0x33, 0x2C,
                 0x89, 0x96, 0xB7, 0xA8, 0xF5, 0xEA, 0xCB, 0xD4],  # 0x3
                [0xA4, 0xBB, 0x9A, 0x85, 0xD8, 0xC7, 0xE6, 0xF9,
                 0x5C, 0x43, 0x62, 0x7D, 0x20, 0x3F, 0x1E, 0x01],  # 0x4
                [0x55, 0x4A, 0x6B, 0x74, 0x29, 0x36, 0x17, 0x08,
                 0xAD, 0xB2, 0x93, 0x8C, 0xD1, 0xCE, 0xEF, 0xF0],  # 0x5
                [0x47, 0x58, 0x79, 0x66, 0x3B, 0x24, 0x05, 0x1A,
                 0xBF, 0xA0, 0x81, 0x9E, 0xC3, 0xDC, 0xFD, 0xE2],  # 0x6
                [0xB6, 0xA9, 0x88, 0x97, 0xCA, 0xD5, 0xF4, 0xEB,
                 0x4E, 0x51, 0x70, 0x6F, 0x32, 0x2D, 0x0C, 0x13],  # 0x7
                [0xEC, 0xF3, 0xD2, 0xCD, 0x90, 0x8F, 0xAE, 0xB1,
                 0x14, 0x0B, 0x2A, 0x35, 0x68, 0x77, 0x56, 0x49],  # 0x8
                [0x1D, 0x02, 0x23, 0x3C, 0x61, 0x7E, 0x5F, 0x40,
                 0xE5, 0xFA, 0xDB, 0xC4, 0X99, 0x86, 0xA7, 0xB8],  # 0x9
                [0x0F, 0x10, 0x31, 0x2E, 0x73, 0x6C, 0x4D, 0x52,
                 0xF7, 0xE8, 0xC9, 0xD6, 0x8B, 0x94, 0xB5, 0xAA],  # 0xA
                [0xFE, 0xE1, 0xC0, 0xDF, 0x82, 0x9D, 0xBC, 0xA3,
                 0x06, 0x19, 0x38, 0x27, 0x7A, 0x65, 0x44, 0x5B],  # 0xB
                [0x2B, 0x34, 0x15, 0x0A, 0x57, 0x48, 0x69, 0x76,
                 0xD3, 0xCC, 0xED, 0xF2, 0xAF, 0xB0, 0x91, 0x8E],  # 0xC
                [0xDA, 0xC5, 0xE4, 0xFB, 0xA6, 0xB9, 0x98, 0x87,
                 0x22, 0x3D, 0x1C, 0x03, 0x5E, 0x41, 0x60, 0x7F],  # 0xD
                [0xC8, 0xD7, 0xF6, 0xE9, 0xB4, 0xAB, 0x8A, 0x95,
                 0x30, 0x2F, 0x0E, 0x11, 0x4C, 0x53, 0x72, 0x6D],  # 0xE
                [0X39, 0x26, 0x07, 0x18, 0x45, 0x5A, 0x7B, 0x64,
                 0xC1, 0xDE, 0xFF, 0xE0, 0xBD, 0xA2, 0x83, 0x9C],  # 0xF
                ]
    # 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
    # 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
    table_C4 = [[0x05, 0x4F, 0x91, 0xDB, 0x2C, 0x66, 0xB8, 0xF2,
                 0x57, 0x1D, 0xC3, 0x89, 0x7E, 0x34, 0xEA, 0xA0],  # 0x0
                [0xA1, 0xEB, 0x35, 0x7F, 0x88, 0xC2, 0x1C, 0x56,
                 0xF3, 0xB9, 0x67, 0x2D, 0xDA, 0x90, 0x4E, 0x04],  # 0x1
                [0x4C, 0x06, 0xD8, 0x92, 0x65, 0x2F, 0xF1, 0xBB,
                 0x1E, 0x54, 0x8A, 0xC0, 0x37, 0x7D, 0xA3, 0xE9],  # 0x2
                [0xE8, 0xA2, 0x7C, 0x36, 0xC1, 0x8B, 0x55, 0x1F,
                 0xBA, 0xF0, 0x2E, 0x64, 0x93, 0xD9, 0x07, 0x4D],  # 0x3
                [0x97, 0xDD, 0x03, 0x49, 0xBE, 0xF4, 0x2A, 0x60,
                 0xC5, 0x8F, 0x51, 0x1B, 0xEC, 0xA6, 0x78, 0x32],  # 0x4
                [0x33, 0x79, 0xA7, 0xED, 0x1A, 0x50, 0x8E, 0xC4,
                 0x61, 0x2B, 0xF5, 0xBF, 0x48, 0x02, 0xDC, 0x96],  # 0x5
                [0xDE, 0x94, 0x4A, 0x00, 0xF7, 0xBD, 0x63, 0x29,
                 0x8C, 0xC6, 0x18, 0x52, 0xA5, 0xEF, 0x31, 0x7B],  # 0x6
                [0x7A, 0x30, 0xEE, 0xA4, 0x53, 0x19, 0xC7, 0x8D,
                 0x28, 0x62, 0xBC, 0xF6, 0x01, 0x4B, 0x95, 0xDF],  # 0x7
                [0x20, 0x6A, 0xB4, 0xFE, 0x09, 0x43, 0x9D, 0xD7,
                 0x72, 0x38, 0xE6, 0xAC, 0x5B, 0x11, 0xCF, 0x85],  # 0x8
                [0x84, 0xCE, 0x10, 0x5A, 0xAD, 0xE7, 0x39, 0x73,
                 0xD6, 0x9C, 0x42, 0x08, 0xFF, 0xB5, 0x6B, 0x21],  # 0x9
                [0x69, 0x23, 0xFD, 0xB7, 0x40, 0x0A, 0xD4, 0x9E,
                 0x3B, 0x71, 0xAF, 0xE5, 0x12, 0x58, 0x86, 0xCC],  # 0xA
                [0xCD, 0x87, 0x59, 0x13, 0xE4, 0xAE, 0x70, 0x3A,
                 0x9F, 0xD5, 0x0B, 0x41, 0xB6, 0xFC, 0x22, 0x68],  # 0xB
                [0xB2, 0xF8, 0x26, 0x6C, 0x9B, 0xD1, 0x0F, 0x45,
                 0xE0, 0xAA, 0x74, 0x3E, 0xC9, 0x83, 0x5D, 0x17],  # 0xC
                [0x16, 0x5C, 0x82, 0xC8, 0x3F, 0x75, 0xAB, 0xE1,
                 0x44, 0x0E, 0xD0, 0x9A, 0x6D, 0x27, 0xF9, 0xB3],  # 0xD
                [0xFB, 0xB1, 0x6F, 0x25, 0xD2, 0x98, 0x46, 0x0C,
                 0xA9, 0xE3, 0x3D, 0x77, 0x80, 0xCA, 0x14, 0x5E],  # 0xE
                [0x5F, 0x15, 0xCB, 0x81, 0x76, 0x3C, 0xE2, 0xA8,
                 0x0D, 0x47, 0x99, 0xD3, 0x24, 0x6E, 0xB0, 0xFA],  # 0xF
                ]
    c = value & 0x0f
    r = (value & 0xf0) >> 4
    if inverse:
        table = table_C4
    else:
        table = table_C3
    return table[r][c]


def testTablesC3and4():
    ok, failed = 0, 0
    ring = BinaryExtensionModulo(getBinaryExtensionRingModulo(8),
                                 variable='z', loglevel=logs)
    for a in range(256):
        b = getRijndaelsAffineMapping(a)
        c = getRijndaelsAffineMapping(b, inverse=True)
        if a != c:
            print("Alert for %4s (%27s):\n"
                  "\ttable C3 say                %4s (%27s) and\n"
                  "\tinverting with table C4 say %4s (%27s)"
                  % (hex(a), ring(a), hex(b), ring(b), hex(c), ring(c)))
            failed += 1
        else:
            ok += 1
    return (ok, failed)


def testAffineMapping(degree=8):
    if degree == 8:
        ok, failed = testTablesC3and4()
        msg = "%d ok %s" % (ok, "but failed %s"
                            % (failed) if failed > 0 else "")
        print("Check with the Rijndael's table c3 and c4: %s\n" % (msg))
        if failed != 0:
            return
    ring = BinaryExtensionModulo(getBinaryExtensionRingModulo(degree),
                                 variable='z', loglevel=logs)
    mu = ring(getMu(degree))
    inv_mu = ~mu
    nu = ring(getNu(degree))
    inv_nu = -nu
    ok, failed = 0, 0
    for i in range(256):
        a = ring(i)
        b = (mu * a) + nu
        bm = (mu.__matrix_product__(a)) + nu
        if degree == 8:
            b_ = getRijndaelsAffineMapping(a._coefficients)
        c = inv_mu * (b + inv_nu)
        cm = inv_mu.__matrix_product__(bm-nu)
        if degree == 8:
            c_ = getRijndaelsAffineMapping(b._coefficients, inverse=True)
        if a != c or b._coefficients != b_:
            if degree == 8:
                about_b = "(table c3 say %4s = %27s)"\
                          % (hex(b_), ring(b_))
                if b._coefficients != b_:
                    about_b += " NOK"
                else:
                    about_b += " OK"
            else:
                about_b = ""
            if degree == 8:
                about_c = "(table c4 say %4s = %27s)"\
                          % (hex(c_), ring(c_))
                if c._coefficients != c_:
                    about_c += " NOK"
                else:
                    about_c += " OK"
            else:
                about_c = ""
            print("Alert for a = %s =     %r:\n"
                  "\tb = (mu*a)+nu =  %27s = %s\t%s\n"
                  "\tc = (~mu*b)-nu = %27s = %s\t%s"
                  % (hex(a._coefficients), a, b, hex(b._coefficients),
                     about_b, c, hex(c._coefficients), about_c))
            failed += 1
        elif a != cm or bm._coefficients != b_:
            if degree == 8:
                about_b = "(table c3 say %4s = %27s)"\
                          % (hex(b_), ring(b_))
                if bm._coefficients != b_:
                    about_b += " NOK"
                else:
                    about_b += " OK"
            else:
                about_b = ""
            if degree == 8:
                about_c = "(table c4 say %4s = %27s)"\
                          % (hex(c_), ring(c_))
                if cm._coefficients != c_:
                    about_c += " NOK"
                else:
                    about_c += " OK"
            else:
                about_c = ""
            print("Matrix alert for a = %s =     %r:\n"
                  "\tb = (mu*a)+nu =  %27s = %s\t%s\n"
                  "\tc = (~mu*b)-nu = %27s = %s\t%s"
                  % (hex(a._coefficients), a, bm, hex(bm._coefficients),
                     about_b, cm, hex(cm._coefficients), about_c))
            failed += 1
        else:
            ok += 1
    print("\nFor degree %d, the affine transfomation has been "
          "b(z) = %s * a(z) + %s. (mu=%s,nu=%s)\n"
          "And the inverse operation                       "
          "a(z) = %s * b(z)+ %s. (~mu=%s,~nu=%s)\n"
          % (degree, mu, nu, hex(mu._coefficients), hex(nu._coefficients),
             inv_mu, inv_nu, hex(inv_mu._coefficients),
             hex(inv_nu._coefficients)))
    return (ok, failed)


def FindRingMus(degree):
    '''
    '''
    modulo = getBinaryExtensionRingModulo(degree)
    ring = BinaryExtensionModulo(modulo)
    idx = 0
    found = 0
    invertibles = []
    inverse_itself = []
    mus = []
    try:
        mu = ring(getMu(degree))
        print("mu=%r" % (mu))
    except:
        print("No mu selected for default")
        mu = None
    while idx < 2**degree:
        sample = ring(idx)
        if sample in invertibles or sample in inverse_itself:
            pass
        else:
            try:
                inv_sample = ~sample
            except:
                pass  # nothing to do with non invertible polynomials
            else:
                try:
                    if sample == inv_sample:
                        inverse_itself.append(sample)
                        found += 1
                    else:
                        invertibles.append(sample)
                        invertibles.append(inv_sample)
                        found += 2
                    if sample == mu:
                        tag = "\t**That is the one in use!**"
                    else:
                        tag = ""
                    print("\tFound %27s with inverse %40r\t(%d - %d 1s) %s"
                          % (sample, inv_sample,
                             bin(sample._coefficients).count('1'),
                             bin(inv_sample._coefficients).count('1'), tag))
                except Exception as e:
                    print("\tAGH! for %s exception: %s" % (sample, e))
        idx += 1
    return found, invertibles, inverse_itself, ring(idx).modulo


def testMusAndNus(degree, mus):
    '''Given a ring size and a list of invertible elements in the ring, check
       which of them (combined with nu candidates) complain the conditions
       to be good pairs of polynomials.
    '''
    import numpy
    modulo = getBinaryExtensionRingModulo(degree)
    ring = BinaryExtensionModulo(modulo, variable='z')
    found = 0
    i = 0
    stats = {}
    print("Start the test of mu(z) and nu(z) candidates for the binary "
          "polynomial ring %s" % (ring(modulo).modulo))
    while i < len(mus):  # for mu in mus:
        mu = ring(mus[i]._coefficients)
        if mu != ring(0) or mu != ring(1):  # mu == 0 or 1, directly discarted
            for j in range(2, 2**degree):
                nu = ring(j)
                testPass, t, tm = testMuAndNu(mu, nu, ring)
                if testPass:
                    found += 1
                    data_t = numpy.array(t)
                    data_tm = numpy.array(tm)
                    if mu.coefficients not in stats:
                        stats[mu.coefficients] = {}
                    if nu.coefficients not in stats[mu.coefficients]:
                        stats[mu._coefficients][nu._coefficients] = {}
                    else:
                        raise("The pair (%s,%s) has been already checked!"
                              % (mu, nu))
                    stats[mu.coefficients][nu.coefficients]['muz'] = "%s" % mu
                    stats[mu.coefficients][nu.coefficients]['nuz'] = "%s" % nu
                    stats[mu.coefficients][nu.coefficients]['product'] = \
                        (data_t.mean(), data_t.std())
                    stats[mu._coefficients][nu.coefficients]['matrix'] = \
                        (data_tm.mean(), data_tm.std())
                    print("Found     "
                          "({},{}) pair: product ({})\tmatrix({})"
                          .format("%27s" % mu, "%27s" % nu,
                                  "%6.6f,%1.5g" % (data_t.mean(),
                                                   data_t.std()),
                                  "%6.6f,%1.5g" % (data_tm.mean(),
                                                   data_tm.std())))
                else:
                    pass  # print("Discarted (%27s,%27s) pair" % (mu, nu))
        i += 1
    return found, stats


def testMuAndNu(mu, nu, ring):
    '''In section 7.2

    Given a polynomial pair of a mu and a nu, check if they complain with
       the conditions:
       - mu: simple description (?)
       - nu: no fixed points neither opposite fixed points
    '''
    import time
    t = []
    tm = []
    for i in range(2**mu.modulodegree):
        a = ring(i)
        t_0 = time.time()
        b = (mu * a) + nu
        t.append(time.time() - t_0)
        t_0 = time.time()
        bm = (mu.__matrix_product__(a)) + nu
        tm.append(time.time() - t_0)
        # check if this three complain the conditions
        if a == b or a == -b:
            return False, None, None
        inv_mu = ~mu
        c = inv_mu * (b + nu)
        if a != c:
            print("Alert! a != c -> %s != %s" % (a, c))
            return False, None, None
        cm = inv_mu.__matrix_product__(bm - nu)
        if a != cm:
            print("Alert! a != cm -> %s != %s" % (a, cm))
            return False, None, None
    return True, t, tm


def findRingInverses(ringSize):
    found, mus, invmu_itself, modulo = FindRingMus(ringSize)
    msg = "\nFound %d invertible polynomials on the ring defined by %s. "\
        "There are %d that their inverse is itself and %d that are different "\
        "(from a total of %d elements in the ring)\n"\
        % (found, modulo, len(invmu_itself), len(mus), 2**ringSize)
    print(msg)
    return found, mus, invmu_itself, modulo


# ## End testing area ----


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                           "{error,warning,info,debug,trace}")
    parser.add_option('', "--binary-polynomial-field", type="int",
                      help="Given a numerical representation of a polynomial "
                      "interpret its bits as coefficients in a binary "
                      "polynomials finite field.")
    parser.add_option('', "--binary-polynomial-ring", type="int",
                      help="Given a numerical representation of a polynomial "
                      "interpret its bits as coefficients in a binary "
                      "polynomials finite ring.")
    parser.add_option('', "--table-c5", action="store_true",
                      help="Test the table C5 from the 'Design of "
                      "Rijndael' book ")
    parser.add_option('', "--test-field", type='int',
                      help="Test all the elements in a field if their product"
                      "with the inverse returns the neutral element z^0")
    parser.add_option('', "--test-all-fields", action="store_true",
                      help="Loops over all available fields doing "
                      "--test-field on it.")
    parser.add_option('', "--test-c3-c4", action="store_true",
                      help="Test the tables C3 and C4 from the 'Design of "
                      "Rijndael' book ")
    parser.add_option('', "--test-affine-mapping", action="store_true",
                      help="Test the finite binary polynomial ring")
    parser.add_option('', "--test-ring", type='int',
                      help="Given the size of the ring (in bits) proceed "
                      "with a search of good parameters for it.")
    parser.add_option('', "--find-ring-inverses", type='int',
                      help="Given the size of a ring (in bits) find all the"
                      "invertible elements.")


def setupLogging(loglevel):
    '''Setup a global variable to know the logging level for all the objects.
    '''
    global logs
    if loglevel is not None:
        logs = _levelFromMeaning(loglevel)
    else:
        logs = _levelFromMeaning('info')

from optparse import OptionParser


def main():
    '''Test the correct functionality of the Polynomial Field and Ring classes.
    '''
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    setupLogging(options.loglevel)
    if options.binary_polynomial_field:
        testBinaryPolynomial(options.binary_polynomial_field)
    if options.binary_polynomial_ring:
        testBinaryPolynomial(options.binary_polynomial_ring, field=False)
    if options.table_c5:
        testC5()
    elif options.test_all_fields:
        import time
        for i in range(16, 1, -1):
            start_t = time.time()
            res = testPolynomialInverse(i)
            end_t = time.time()
            print("For F_{2^%d}, test elements:\t%s\t(%gseconds)"
                  % (i, res, end_t - start_t))
        print("\n")
    elif options.test_field:
        ok, failed = testPolynomialInverse(options.test_field)
        msg = "%d ok %s" % (ok, "but failed %s"
                            % (failed) if failed > 0 else "")
        print("For F_{2^%d}, test elements: %s\n"
              % (options.test_field, msg))
    elif options.test_c3_c4:
        ok, failed = testTablesC3and4()
        msg = "%d ok %s" % (ok, "but failed %s"
                            % (failed) if failed > 0 else "")
        print("Check with the Rijndael's table c3 and c4: %s\n" % (msg))
    elif options.test_affine_mapping:
        ok, failed = testAffineMapping()
        msg = "%d ok %s" % (ok, "but failed %s"
                            % (failed) if failed > 0 else "")
        print("Check the binary polynomial ring: %s" % (msg))
    elif options.find_ring_inverses is not None:
        findRingInverses(options.find_ring_inverses)
    elif options.test_ring is not None:
        found, mus, invmu_itself, modulo = findRingInverses(options.test_ring)

        import time
        when = time.strftime("%Y%m%d_%H%M%S")
        fileName = "%s_ring_degree_%d.csv" % (when, options.test_ring)
        print("Proceeding with a search of mu(z) and nu(z) candidates. "
              "This is a long process that will provide as an output a"
              "csv file called: %s" % (fileName))
        t_0 = time.time()
        found, stats = testMusAndNus(options.test_ring, mus+invmu_itself)
        msg = "Search compleated. Found %d pairs of valid mus and nus "\
            "(%d seconds)" % (found, time.time()-t_0)
        print(msg)
        with open(fileName, 'w') as f:
            f.write("mu\tnu\tmuz\tnuz\t"
                    "product_mean\tproduct_std\tmatrix_mean\tmatrix_std\n")
            for i in stats.keys():
                for j in stats[i].keys():
                    stats[i][j]['muz']
                    stats[i][j]['nuz']
                    line = "%d\t%d\t%s\t%s\t%g\t%g\t%g\t%g\n"\
                           % (i, j, stats[i][j]['muz'], stats[i][j]['nuz'],
                              stats[i][j]['product'][0],
                              stats[i][j]['product'][1],
                              stats[i][j]['matrix'][0],
                              stats[i][j]['matrix'][1])
                    f.write(line)
    else:
        print("\n\tNo option specified, please check with -h or --help\n")

if __name__ == "__main__":
    main()
