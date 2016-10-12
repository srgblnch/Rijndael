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

from BinaryPolynomials import *
from PolynomialRing import *

try:
    from ..Logger import Logger as _Logger
except:
    from Logger import Logger as _Logger
from random import randint


# Testing ----


def randomBinaryPolynomial(field, degree):
    return field(randint(0, 2**degree))


def randomPolynomial(ring, ringDegree, field, fieldDegree):
    coefficients = []
    for i in range(ringDegree):
        coefficients.append(randomBinaryPolynomial(field, fieldDegree))
    return ring(coefficients)


def testConstructor():
    print("Use PolynomialsTest.py for testing.")
    field = BinaryExtensionModulo('z^8+z^4+z^3+z+1', loglevel=_Logger._info)
    ring = PolynomialRingModulo("x^4+1", field, loglevel=_Logger._debug)
    example = randomPolynomial(ring, 4, field, 8)
    print("Random element of the polynomial ring with coefficients in a "
          "binary polynomial field:\n\tstring:\t%s\n\trepr:\t%r\n\thex:\t%s"
          % (example, example, hex(example)))
    example._coefficients[randint(0, 3)] = field(0)
    print("Eliminate one of the coefficients to test the good representation "
          "when there is no coefficient:\n\tstring:\t%s\n\trepr:\t%r"
          "\n\thex:\t%s" % (example, example, hex(example)))
    try:
        ring = PolynomialRingModulo("z^4+1", field, variable='zs')
    except:
        print("Constructor multichar lenght variable:\tpass.")
    else:
        print("Alert! Build a polynomial modulo with an invalid variable name")
    try:
        ring = PolynomialRingModulo("z^4+1", field, variable='z')
    except:
        print("Constructor with two equal variable:\tpass.")
    else:
        print("Alert! Build a polynomial modulo with the same vble name for "
              "coefficients test failed.")


def testAdd(a=None, b=None):
    field = BinaryExtensionModulo('z^8+z^4+z^3+z+1', loglevel=_Logger._info)
    ring = PolynomialRingModulo("x^4+1", field, loglevel=_Logger._debug)
    if a is None:
        a = randomPolynomial(ring, 4, field, 8)
    elif type(a) == list:
        a = ring([field(a[i]) for i in range(len(a))])
    if b is None:
        b = randomPolynomial(ring, 4, field, 8)
    elif type(b) == list:
        b = ring([field(b[i]) for i in range(len(b))])
    c = a + b
    print("Test to add %s + %s = %s" % (hex(a), hex(b), hex(c)))


def doProductTest(axlist=None, sxlist=None):
    field = BinaryExtensionModulo('z^8+z^4+z^3+z+1', loglevel=_Logger._info)
    ring = PolynomialRingModulo("x^4+1", field, loglevel=_Logger._info)
    if axlist is None:
        axlist = []
        for i in range(4):
            axlist.append(randint(0, 2**8))
        axrandom = True
    else:
        axrandom = False
    if sxlist is None:
        sxlist = []
        for i in range(4):
            sxlist.append(randint(0, 2**8))
        sxrandom = True
    else:
        sxrandom = False
    ax = ring([field(i) for i in axlist])
    sx = ring([field(i) for i in sxlist])
#     if axrandom and sxrandom:
#         print("Testing random pair: %s * %s" % (hex(ax), hex(sx)))
#     elif axrandom:
#         print("Testing pair with first term random: %s * %s"
#               % (hex(ax), hex(sx)))
#     elif sxrandom:
#         print("Testing pair with second term random: %s * %s"
#               % (hex(ax), hex(sx)))
#     else:
#         print("Testing fixed pair: %s * %s" % (ax, sx))
#     print("\tVector representation or the pair: [%s] * [%s]"
#           % ("".join(" 0x%X," % (e for e in axlist)[1:-1]),
#              "".join(" 0x%X," % (e for e in sxlist)[1:-1])))
    rx = ax * sx
    bar = PolynomialRing(4, 4, 8)
    state = [sxlist]*4
    foo = bar.product(axlist, state)
    foox = ring([field(i) for i in foo[0]])
    if rx != foox:
        print("\t\tError!! Results using "
              "PolynomialRingModulo != PolynomialRing "
              "implementations:\n\t\t\t%s != %s" % (hex(rx), hex(foox)))
        return (False, "Error")
    else:
        if sx == rx:
            print("\t\tAlert s(x) == r(x), when r(x) = a(x) * s(x)\n"
                  "\t\t\tr(x) = %s = %s\n"
                  "\t\t\ts(x) = %s = %s\n"
                  "\t\t\ta(x) = %s = %s"
                  % (hex(rx), rx, hex(sx), sx, hex(ax), ax))
            return (False, "Alert")
        else:
            # print("\t\tOK: r(x) = %s" % (hex(rx)))
            return (True, "")


def productByInverse(polynomial, inverse=None):
    field = BinaryExtensionModulo('z^8+z^4+z^3+z+1', loglevel=_Logger._info)
    ring = PolynomialRingModulo("x^4+1", field, loglevel=_Logger._info)
    productNeutralElement = ring([field(1)])
    if inverse is None:
        inverse = ~polynomial
    rx = polynomial * inverse
    # rx.reduce()
    if rx != productNeutralElement:
        print("Alert! Does polynomials doesn't produce the neutral")
        return False
    else:
        print("Polynomial product by its inverse results the neutral!")
    return True


def testProduct(n):
    header = "Testing the product operation"
    stars = "*"*(len(header)+1)
    print("\n%s\n%s:\n%s\n" % (stars, header, stars))
#     field = BinaryExtensionModulo('z^8+z^4+z^3+z+1', loglevel=_Logger._info)
#     ring = PolynomialRingModulo("x^4+1", field, loglevel=_Logger._debug)
#     c_x = ring('(z+1)*x^3+x^2+x+(z)')
#     d_x = ring('(z^3+z+1)*x^3+(z^3+z^2+1)*x^2+(z^3+1)*x+(z^3+z^2+z)')
#     productByInverse(polynomial=c_x, inverse=d_x)
    print("="*80)
    errors = 0
    alerts = 0
    for r in range(n):
        ok, reason = doProductTest()
        if not ok and reason == "Error":
            errors += 1
        if not ok and reason == "Alert":
            alerts += 1
    print("="*80)
    if errors > 0:
        print("There has been %g%% errors (%d/%d)"
              % (float(errors)/n*100, errors, n))
    if alerts > 0:
        print("There has been %g%% alerts (%d/%d)"
              % (float(alerts)/n*100, alerts, n))
    print("")
#     doProductTest(axlist=[3, 1, 1, 2], sxlist=[0xB, 0xD, 0x9, 0xE])
#     for r in range(n):
#         # if not doProductTest(axlist=[0xB, 0xD, 0x9, 0xE]): break
#         if not doProductTest(axlist=[3, 1, 1, 2]): break


def main():
    # FIXME: this should have commandline arguments to specify
    # what shall be tested
    # testConstructor()
    # testAdd(a=[0xAA, 0xAB, 0xAC, 0xAD], b=[1, 1, 1, 1])
    # testAdd()
    testProduct(2000)

if __name__ == "__main__":
    from random import randint
    main()
