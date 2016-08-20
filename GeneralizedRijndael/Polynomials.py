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

from copy import copy as _copy
from copy import deepcopy as _deepcopy
from Logger import Logger as _Logger
from random import randint
from ThirdLevel import shift as _shift

# FIXME: remove!
from time import sleep
import traceback


def BinaryExtensionModulo(modulo, variable='z', loglevel=_Logger._info):
    '''
        BinaryExtensionModulo is a builder for \mathbb{F}_{2^w} (or GF(2^w) in
        another notation) elements. Finite field or ring with characteristic 2
        and extension degree 8, build from the polynomial ring F_2[z] modulo
        a degree w polynomial. This will produce a field if the modulo
        polynomial is irreduceble or a ring in case it can be reduced.

        The integer representation will use binary representation to assign
        the MSB to highest degree and the LSB to the 0 degree. For the string
        representation the sage notation has been take as inspiration.

        Arguments:
        - modulo: (mandatory) an integer or an string representation of a
          polynomial (like 'z^8+z^4+z^3+z+1' that's equivalent to 0x11B).
        - variable: by default is 'z' and it is only used for the output
          strings representing the polynomials.
        - loglevel: by default info, based on the superclass Logger
          enumeration.

        Example:
        >>> import Polynomials
        >>> field = Polynomials.BinaryExtensionModulo('z^8+z^4+z^3+z+1')
    '''
    # This help is shown when
    # >>> Polynomials.BinaryExtensionModulo?
    if len(variable) != 1:
        raise NameError("The indeterminate must be a single character.")
    if ord('a') > variable.lower() > ord('z'):
        raise NameError("The indeterminate must be a valid alphabet letter.")
    if type(modulo) == str and modulo.count(variable) == 0:
        raise Exception("modulo %s is not defined over %s variable"
                        % (modulo, variable))

    class BinaryExtensionModuloConstructor(_Logger):
        def __init__(self, value, *args, **kwargs):
            '''
                Once have the builder of elements it can be used to generate
                objects that represents and have operations defined. The allow
                representations are integers (to be represented as a list of
                coefficients in binary) or a string representation with
                polynomial notation.

                Argument:
                - value: (mandatory) the value to be interpreted as a binary
                  polynomial finite field or ring.

                Example:
                >>> from Polynomials import BinaryExtensionModulo
                >>> field = BinaryExtensionModulo('z^8+z^4+z^3+z+1')
                >>> a = field(73); a
                z^6+z^3+1 (mod z^8+z^4+z^3+z+1)
            '''
            # This help is shown when, from the last one
            # >>> field?
            # FIXME: improve the logging on this class
            super(BinaryExtensionModuloConstructor, self).__init__(*args,
                                                                   **kwargs)
            self._variable = variable
            if type(value) == BinaryExtensionModuloConstructor or \
               value.__class__ == BinaryExtensionModuloConstructor:
                self._coefficients = value.coefficients
            elif type(value) == int:
                self._coefficients = abs(value)
            elif type(value) == str:
                self._coefficients = self.__interpretFromStr__(value)
            else:
                try:  # Do a last try to interpret the coefficients
                    self._coefficients = int(value)
                except Exception as e:
                    raise AssertionError("The given coefficients type '%s'"
                                         "is not interpretable"
                                         % (type(value)))
            self._gcd = None
            self._multinv = None
            self._debug_stream("coefficients", self._coefficients)
            if type(modulo) == int:
                self._modulo = modulo
            elif type(modulo) == str:
                self._modulo = self.__interpretFromStr__(modulo)
            else:
                try:  # Do a last try to interpret the coefficients
                    self._modulo = int(modulo)
                except Exception as e:
                    raise AssertionError("The given modulo type '%s'"
                                         "is not interpretable"
                                         % (type(modulo)))
            self._debug_stream("modulo", self._modulo)
            # if the degree of coefficients > degree of modulo,
            # do the reduction
            if self.degree >= len("{0:b}".format(self._modulo)):
                q, r = self.__division__(self._coefficients, self._modulo)
                self._coefficients = r
                self._debug_stream("reduced coefficients", self._coefficients)

        @property
        def coefficients(self):
            """Get the coefficients of the polinomial as an integer"""
            return self._coefficients

        @property
        def modulo(self):
            """Get the string that represents the modulo polynomials"""
            return self.__interpretToStr__(self._modulo)

        @property
        def variable(self):
            """Get the char that is used as polinomial variable."""
            return self._variable

        @property
        def degree(self):
            """Get the degree of the polynomial"""
            return len("{0:b}".format(self._coefficients))

        @property
        def hammingWeight(self):
            """Get the hamming weight of the polynomial.
               Hamming weight is defined as the number of non null elements. In
               the binary case, the number of ones.
            """
            return bin(self._coefficients).count('1')

        @property
        def modulodegree(self):
            """Get the degree of the modulo polynomial. That is the maximum
               that the elements on the field/ring defined could have.
            """
            return len("{0:b}".format(self._modulo))

        @property
        def isZero(self):
            '''Neutral element of the first operation, addition.'''
            return self._coefficients == 0

        @property
        def isOne(self):
            '''Neutral element of the second operation, product.'''
            return self._coefficients == 1

        @property
        def isInvertible(self):
            '''Show if the element is invertible modulo for the product
               operation.
            '''
            if self._gcd is None:
                self._gcd, self._multinv, y = self.__egcd__(self._coefficients,
                                                            self._modulo)
            if self._gcd == 1:
                return True
            return False

        def __iter__(self):
            return iter("{0:b}".format(self._coefficients))

        def iter(self):
            return self.__iter__()

        def __getitem__(self, n):
            mask = 1 << n
            if self._coefficients & mask:
                return 1
            else:
                return 0

        def __type__(self):
            return self.__class__

        def checkTypes(function):
            '''Decorator to precheck the input parameters on some of the
               operations.
            '''
            def comparator(self, other):
                if other.__class__ in [type(None), int]:
                    return function(self, other)
                if str(other.__class__) != str(self.__class__):
                    raise EnvironmentError("Cannot compare with non "
                                           "polynomials (%s,%s)"
                                           % (type(other), other.__class__))
                if not self.variable == other.variable:
                    raise EnvironmentError("Uncompatible polynomials")
                if not self._modulo == other._modulo:
                    raise EnvironmentError("Those polynomials are not in the "
                                           "same equivalence class")
                return function(self, other)
            return comparator

        def __str__(self):
            '''Readable representation. (%s)
            '''
            return self.__interpretToStr__(self._coefficients)

        def __repr__(self):
            # FIXME: temporally remove the modulo to clear egcd debugging
            '''Unambiguous representation. (%r)
            '''
            # return "%s (mod %s)"\
            #     % (self.__interpretToStr__(self._coefficients),
            #        self.__interpretToStr__(self._modulo))
            return self.__str__()

        def __bin__(self):
            # TODO: doesn't work, check it
            return bin(self._coefficients)

        def __oct__(self):
            return oct(self._coefficients)

        def __hex__(self):
            return hex(self._coefficients)

        def __interpretToStr__(self, value):
            if value == 0:
                return '0'  # FIXME: the neutral element of the first operation
            else:
                terms = []  # coefficients representations list
                bitlist = "{0:b}".format(value)
                # FIXME: Improve this dirtied casuistry... Not efficient.
                for idx, coefficient in enumerate(bitlist):
                    exponent = len(bitlist)-idx-1
                    if coefficient == '0':
                        terms.append('')
                    elif exponent == 0:  # and coefficient == '1'
                        terms.append('+1')
                    elif exponent == 1:  # and coefficient == '1'
                        # equiv to z^1 but short
                        terms.append('+%s' % (self._variable))
                    else:
                        terms.append('+%s^%d' % (self._variable, exponent))
                collect = ''.join(["%s" % (r) for r in terms])
                if collect[0] == '+':  # remove the first sign if present
                    collect = collect[1:]
                return collect

        def __interpretFromStr__(self, string):
            terms = string.strip().split('+')
            value = 0
            for i in range(len(terms)):
                if terms[i] == '%s' % self._variable:
                    value |= 1 << 1  # z^1
                elif terms[i] == '1':
                    value |= 1
                elif terms[i].count(self._variable):
                    exponent = int(terms[i].split('%s^' % self._variable)[1])
                    value |= 1 << exponent
                else:
                    raise SyntaxError("the term %s cannot be interpreted"
                                      % (terms[i]))
            return value

        def __abs__(self):
            return BinaryExtensionModuloConstructor(abs(self._coefficients))

        def __len__(self):
            bits = "{0:b}".format(self._coefficients)
            if bits[0] == '-':
                bits = bits[1:]
            return len(bits)

        @checkTypes
        def __eq__(self, other):  # => a == b
            if other is None:
                return False
            if self._coefficients == other._coefficients:
                return True
            return False

        @checkTypes
        def is_(self, other):  # => a == b
            return self == other

        @checkTypes
        def __ne__(self, other):  # => a!=b
            if self.__eq__(other):
                return False
            return True

        @checkTypes
        def is_not(self, other):  # => a != b
            return self != other

        # Meaningless operators in polynomials:
        # operator.__lt__(a,b) => a<b
        # operator.__le__(a,b) => a<=b
        # operator.__gt__(a,b) => a>b
        # operator.__ge__(a,b) => a>=b
        # #Operations ----
        # + Addition ----

        @checkTypes
        def __add__(self, other):  # => a+b
            a = _copy(self.coefficients)
            b = _copy(other.coefficients)
            return BinaryExtensionModuloConstructor(a ^ b)

        def __iadd__(self, other):  # => a += b
            bar = self + other
            return BinaryExtensionModuloConstructor(bar._coefficients)

        def __pos__(self):  # => +a
            return self

        # - Substraction ----

        def __neg__(self):  # => -a
            return self

        def __sub__(self, other):  # => a-b
            # bar = -other it is itself
            a = _copy(self.coefficients)
            b = _copy(other.coefficients)
            return BinaryExtensionModuloConstructor(a ^ b)

        def __isub__(self, other):  # => a-=b
            bar = self - other
            return BinaryExtensionModuloConstructor(bar._coefficients)

        # * Product ----

        @checkTypes
        def __mul__(self, other):  # => a*b
            '''
            '''
            if type(other) == int:  # a * n = [a, a,..., a]
                res = []
                for i in range(other):
                    res.append(_deepcopy(self))
                return res
            a = _copy(self._coefficients)
            b = _copy(other._coefficients)
            res = self.__multiply__(a, b)
            self._debug_stream("c = a * b = %s * %s = %s"
                               % (self.__interpretToStr__(a),
                                  self.__interpretToStr__(b),
                                  self.__interpretToStr__(res)))
            return BinaryExtensionModuloConstructor(res)

        def __imul__(self, other):  # => a*=b
            bar = self * other
            return BinaryExtensionModuloConstructor(bar._coefficients)

        def xtimes(self):
            return self << 1

        def __multiply__(self, a, b):
            '''Given the coefficients of two valid polynomials, interpret the
               integers as bit strings to proceed with a polynomial product
               (without reduction).
               With the goal of a constant time operation, the number of loops
               to manage each of the coefficients in b(z) will be always the
               maximum (that is, the based on the reduction polynomio. Also
               there will be performed the same operations even the coefficient
               in the loop to process is 0 or 1 (and the distinction is on the
               value returned from the submethod __multiplicationStep__().
               Input: <integer> a (multiplicand)
                      <integer> b (multiplier)
               Output: <integer> (result of the polynomial product).
            '''
            self._debug_stream("a %s" % self.__interpretToStr__(a))
            self._debug_stream("b %s" % self.__interpretToStr__(b))
            result = 0
            mask = 1
            i = 0
            while mask < self._modulo:
                bit = b & mask
                result = self.__multiplicationStep__(a, bit, i, result)
                mask <<= 1
                i += 1
            return result

        def __multiplicationStep__(self, a, bit, i, accum):
            '''Constant time function to calculate one of the steps in the
               multiplication.
               Input: <integer> a (the first element of the product)
                      <boolean> bit (the bit of b on the step)
                      <integer> i (the exponent where 'bit' is located)
                      <integer> accum (partial result from previous steps)
               Output: <integer> (the accumulated result of the product)
            '''
            aShifted = a << i
            newerAccum = accum ^ aShifted
            if bit:
                self._debug_stream("aShifted: %s"
                                   % self.__interpretToStr__(aShifted))
                return newerAccum
            else:
                return accum

        def __matrix_product__(self, other):
            '''In equivalence to the product operation, there is another way
               to do this operation by interpret the polynomials in GF(2^w)
               or a ring of this grade, as bit arrays in GF(2)^w.
               Then proceed with a matrix product converting the first term in
               a MDS (Maximum Distance Separable) matrix using the bit
               rotation.
               Self is converted like:
               [[ 0   w  w-1 w-2 ... 1],
                [ 1   0   w  w-1 ... 2],
                [          ...        ],
                [w-1 w-2 w-3 w-4 ... w],
                [ w  w-1 w-2 w-3 ... 0]]
                and other like:
                [0,1,...,w-1,w]
                Having a matrix wxw and a vector wx1, the result is a matrix
                mx1 that can be back interpreted each bit as the coeffiecient
                in a polynomial GF(2^w) if it was irreducible modulo or a ring.
            '''
            self._debug_stream("self * other: %r * %r = %s * %s"
                               % (self, other, bin(self._coefficients),
                                  bin(other._coefficients)))
            # self._coefficients in binary corresponds to last row
            # 1 shift to the left is row0
            row = self._cyclic_rshift_(1)
            res = 0
            self._debug_stream("input: %s %r"
                               % (bin(other._coefficients), other))
            input = self.__mirrorbits__(other._coefficients)
            for i in range(self.modulodegree-1):
                res = res << 1
                self._debug_stream("row[%d]: %s %r"
                                   % (i, bin(row._coefficients), row))
                bitProduct = row._coefficients & input
                parity = self.__parity__(bitProduct)
                row = row._cyclic_rshift_(1)
                res |= parity
            self._debug_stream("result: %s" % (bin(res)))
            return BinaryExtensionModuloConstructor(self.__mirrorbits__(res))

        def __parity__(self, bits):
            '''Given a number, use a bit representation to proceed with an xor
               (addition in GF(2)) of each of its elements.
            '''
            msg = "parity = %s" % (bin(bits))
            while bits > 1:
                bits = (bits >> 1) ^ (bits & 1)
            self._debug_stream("%s = %d" % (msg, bits))
            return bits

        def __mirrorbits__(self, bits):
            '''Exchange the bit significance by placing the LSB first and the
               MSB at the end.
            '''
            maxbits = self.modulodegree-1
            origin = bits
            mirror = 0
            for i in range(maxbits):  # while bits > 0:
                mirror <<= 1
                mirror |= origin & 1
                origin >>= 1
            self._debug_stream("mirrored %s to %s"
                               % (bin(bits), bin(mirror)))
            return mirror

        # /% Division ----

        def __division__(self, divident, divisor):
            '''
               Given two polynomials, divide them and return its quotient
               and rest.
               Input: Two polynomial elements.
               Output: The quotient and rest between the two input polynomials.
            '''
            if divisor == 0:
                raise ZeroDivisionError
            self._debug_stream("\n<division>")
            gr_divident = len("{0:b}".format(divident))-1
            gr_divisor = len("{0:b}".format(divisor))-1
            quotient = 0
            rest = divident
            self._debug_stream("divident", divident)
            self._debug_stream("divisor", divisor)
            self._debug_stream("quotient", quotient)
            self._debug_stream("rest", rest)
            shift = gr_divident-gr_divisor
            while len("{0:b}".format(rest)) >= len("{0:b}".format(divisor)) \
                    and shift >= 0:
                # FIXME: this means deg(rest) >= deg(divisor),
                #        but it's horrible
                gr_rest = len("{0:b}".format(rest))-1
                if shift > 0:
                    temp = int("{0:b}".format(rest)[0:-shift], 2) << shift
                else:
                    temp = rest
                self._debug_stream("temp", temp)
                subs = divisor << shift
                self._debug_stream("subs", subs)
                if len("{0:b}".format(temp)) == len("{0:b}".format(subs)):
                    bar = temp ^ subs
                    self._debug_stream("temp ^subs", bar)
                    if shift > 0:
                        mask = int('1'*shift, 2)
                        quotient = quotient | 1 << (shift)
                        rest = bar | (divident & mask)
                    else:
                        quotient |= 1
                        rest = bar
                self._debug_stream("quotient", quotient)
                self._debug_stream("rest", rest)
                gr_divident -= 1
                shift = gr_divident-gr_divisor
            self._debug_stream("<\\division>\n")
            return (quotient, rest)

        def __div__(self, other):  # => a/b
            q, r = self.__division__(self._coefficients, other._coefficients)
            return BinaryExtensionModuloConstructor(q)
            # FIXME: the constructor will reduce it having the rest
            #        and not the quotient

        def __idiv__(self, other):  # => a/=b
            q, r = self.__division__(self._coefficients, other._coefficients)
            return BinaryExtensionModuloConstructor(q)

        def __mod__(self, other):  # => a%b
            q, r = self.__division__(self._coefficients, other._coefficients)
            return BinaryExtensionModuloConstructor(r)

        def _imod__(self, other):  # => a%=b
            q, r = self.__division__(self._coefficients, other._coefficients)
            return BinaryExtensionModuloConstructor(r)

        # ~ Multiplicative inverse ----
        # - operator.__inv__(a) => ~a

        def __egcd__(self, a, b):
            '''Extended Euclidean gcd (Greatest Common Divisor) Algorithm
               From Hankerson,Menezes,Vanstone "Guide to Elliptic Curve
               Cryptography" Algorithm 2.47.
               Input: <integer> a (polynomial bit representation)
                      <integer> b (polynomial bit representation)
               Output: <integer> gcd
                       <integer> x (polynomial bit representation)
                       <integer> y (polynomial bit representation)
            '''
            u, v = a, b
            self._debug_stream("u", u)
            self._debug_stream("v", v)
            g1, g2, h1, h2 = 1, 0, 0, 1
            self._debug_stream("g1", g1)
            self._debug_stream("g2", g2)
            self._debug_stream("h1", h1)
            self._debug_stream("h2", h2)
            while u != 0:
                j = len("{0:b}".format(u))-len("{0:b}".format(v))
                if j < 0:
                    self._debug_stream("%d < 0" % j)
                    # u <-> v
                    u, v = v, u
                    # g1 <-> g2
                    g1, g2 = g2, g1
                    # h1 <-> h2
                    h1, h2 = h2, h1
                    j = -j
                u = u ^ (v << j)
                g1 = g1 ^ (g2 << j)
                h1 = h1 ^ (h2 << j)
                self._debug_stream("\tu", u)
                self._debug_stream("\tg1", g1)
                self._debug_stream("\th1", h1)
            d, g, h = v, g2, h2
            self._debug_stream("d", d)
            self._debug_stream("g", g)
            self._debug_stream("h", h)
            return d, g, h

        @checkTypes
        def __gcd__(self, other):
            a = self._coefficients
            b = other._coefficients
            gcd, x, y = self.__egcd__(a, b)
            return gcd

        # ~ Multiplicative inverse: ----
        #        - operator.__inv__(a) => ~a
        def __invert__(self):  # => ~a, that means like a^-1
            res = self.__multiplicativeInverse__()
            return BinaryExtensionModuloConstructor(res)

        def __multiplicativeInverse__(self):
            '''Multiplicative inverse based on ...
               Input: <integer> a (polynomial bit representation)
                      <integer> m (modulo polynomial)
               Output: <integer> a^-1: a*a^-1 = 1 (mod m)
               This it the first of the two transformations for the SBoxes
               in the subBytes operation, the one called called g.
            '''
            if self._coefficients == 0:  # FIXME: is this true?
                return self
            if self._gcd is None:
                self._gcd, self._multinv, y = \
                    self.__egcd__(self._coefficients, self._modulo)
            self._debug_stream("gcd", self._gcd)
            self._debug_stream("x", self._multinv)
            if self._gcd != 1:
                bar = self.__interpretToStr__(self._coefficients)
                foo = self.__interpretToStr__(self._modulo)
                raise ArithmeticError("The inverse of %s modulo %s "
                                      "doens't exist!"
                                      % (bar, foo))
            else:
                return self._multinv  # % self._modulo

        # <<>> Shifts ----
        def __lshift__(self, n):  # => <<
            return BinaryExtensionModuloConstructor(self._coefficients << n)

        def __rshift__(self, n):  # => >>
            return BinaryExtensionModuloConstructor(self._coefficients >> n)

        def __ilshift__(self, n):  # => <<=
            return BinaryExtensionModuloConstructor(self._coefficients << n)

        def __irshift__(self, n):  # => >>=
            return BinaryExtensionModuloConstructor(self._coefficients >> n)

        def _cyclic_lshift_(self, n):
            '''
            '''
            return BinaryExtensionModuloConstructor(self._bit_lshift_(n))

        def _bit_lshift_(self, n):
            '''Using the polynomial coefficients as a bit string, return a bit
               string with a left side cyclic shift. It uses the modulo degree
               to do this shift within this length.
            '''
            maxbits = self.modulodegree-1
            first = (self._coefficients << n % maxbits) & 2**maxbits-1
            second = (self._coefficients >> (maxbits-(n % maxbits))
                      & 2**maxbits-1)
            return first | second

        def _cyclic_rshift_(self, n):
            '''
            '''
            return BinaryExtensionModuloConstructor(self._bit_rshift_(n))

        def _bit_rshift_(self, n):
            '''Using the polynomial coefficients as a bit string, return a bit
               string with a right side cyclic shift. It uses the modulo
               degree to do this shift within this length.
            '''
            maxbits = self.modulodegree-1
            first = (self._coefficients >> n % maxbits) & 2**maxbits-1
            second = (self._coefficients << (maxbits-(n % maxbits))
                      & 2**maxbits-1)
            return first | second
        # End class BinaryExtensionModuloConstructor ----
    return BinaryExtensionModuloConstructor


def getBinaryExtensionFieldModulo(wordSize):
    '''Who is chosen m(z)? [1] z^8+z^4+z^3+z+1 is the first that those the job
       (build a polynomial field), and that is the rule for the other sizes
       under study here.
       [1] "http://crypto.stackexchange.com/questions/16017/"\
           "about-the-rijndael-aes-sbox-polynomial-subbytes"
    '''
    BinaryExtensionFieldModulo = {
        2: 0x07,  # z^2+z+1
        3: 0x0B,  # z^3+z+1
        4: 0x13,  # z^4+z+1
        5: 0x25,  # z^5+z^2+1
        6: 0x43,  # z^6+z+1
        7: 0x83,  # z^7+z+1
        8: 0x11B,  # z^8+z^4+z^3+z+1 the Rijndael's original
        9: 0x203,  # z^9+z+1
        10: 0x409,  # z^10+z^3+1
        11: 0x805,  # z^11+z^2+1
        12: 0x1009,  # z^12+z^3+1
        13: 0x201B,  # z^13+z^4+z^3+z+1
        14: 0x4021,  # z^14+z^5+1
        15: 0x8003,  # z^15+z+1
        16: 0x1002B,  # z^16+z^5+z^3+z+1
    }[wordSize]
    return BinaryExtensionFieldModulo


def getBinaryExtensionRingModulo(wordSize):
    '''Who is chosen m'(z)? z^8+1 is the first that those the job
       (build a polynomial ring), and that is the rule for the other sizes
       under study here.
       This is quite similar to how the binary polynomial field modulo is
       chosen.
    '''
    BinaryExtensionRingModulo = {
        2: 0x05,  # z^2+1
        3: 0x09,  # z^3+1
        4: 0x11,  # z^4+1
        5: 0x21,  # z^5+1
        6: 0x41,  # z^6+1
        7: 0x81,  # z^7+1
        8: 0x101,  # z^8+1 the Rijndael's original
        9: 0x201,  # z^9+1
        10: 0x401,  # z^10+1
        11: 0x801,  # z^11+1
        12: 0x1001,  # z^12+1
        13: 0x2001,  # z^13+1
        14: 0x4001,  # z^14+1
        15: 0x8001,  # z^15+1
        16: 0x10001,  # z^16+1
    }[wordSize]
    return BinaryExtensionRingModulo


def getMu(wordSize, official=False):
    '''Invertible element in the binary polynomial ring used in the second
       transformation 'f' of the SBoxes.
       b(z) = mu(z) \cdot a(z) + nu(z)
       When undo the transformation:
       a(z) = mu^{-1}(z) \cdot [b(z) - nu(z)]
    '''
    if official and wordSize == 8:
        return 0x1F
    Mu = {
        3: 0x02,  # z
        4: 0x07,  # z^2+z+1
        5: 0x0B,  # z^3+z+1
        6: 0x0D,  # z^3+z^2+1
        7: 0x26,  # z^5+z^2+z
        8: 0x3D,  # z^5+z^4+z^3+z^2+1#0x1F,#z^4+z^3+z^2+z+1
        9: 0x52,  # z^6+z^4+z
        10: 0x15C,  # z^8+z^6+z^4+z^3+z^2
        11: 0x6C8,  # z^10+z^9+z^7+z^6+z^3
        12: 0xEC6,  # z^11+z^10+z^9+z^7+z^6+z^2+z
        13: 0x1D2A,  # z^12+z^11+z^10+z^8+z^5+z^3+z
        14: 0x3CC2,  # z^13+z^12+z^11+z^10+z^7+z^6+z
        15: 0x79A0,  # z^14+z^13+z^12+z^11+z^8+z^7+z^5
        16: 0xFAE0,  # $z^15+z^14+z^13+z^12+z^11+z^9+z^7+z^6+z^5
    }[wordSize]
    return Mu


def getNu(wordSize, official=False):
    '''Element of the binary polynomial ring used in the second transformation
       'f' of the SBoxes:
       b(z) = mu(z) \cdot a(z) + nu(z)
       When undo the transformation:
       a(z) = mu^{-1}(z) \cdot [b(z) - nu(z)]
    '''
    if official and wordSize == 8:
        return 0x63
    Mu = {
        3: 0x02,  # z
        4: 0x08,  # z^3
        5: 0x02,  # z
        6: 0x2C,  # z^5+z^3+z^2
        7: 0x10,  # z^4
        8: 0x47,  # z^6+z^2+z+1#0x63,#z^6+z^5+z+1
        9: 0x3A,  # z^5+z^4+z^3+z
        10: 0x236,  # z^9+z^5+z^4+z^2+z
        11: 0xAD,  # z^7+z^5+z^3+z^2+1
        12: 0x53,  # z^6+z^4+z+1
        13: 0x22b,  # z^9+z^5+z^3+z+1
        14: 0x38CC,  # z^13+z^12+z^11+z^7+z^6+z^3+z^2
        15: 0x9D9,  # z^11+z^8+z^7+z^6+z^4+z^3+1
        16: 0x30FA,  # z^13+z^12+z^7+z^6+z^5+z^4+z^3+z
    }[wordSize]
    return Mu


def PolynomialRingModulo(modulo, coefficients_class, variable='x',
                         loglevel=_Logger._info):
    '''
        PolynomialRingModulo is a builder for (\mathbb{F}_{2^w})^l (or
        (GF(2^w))^l in another notation) elements. This is a polynomial made
        by l elements of a finite field of characteristic 2 with an
        extension degree w. This polynomial is made modulo a polynomial with
        l degree producing ring. But it could generate a field depending on
        the irreducibility or not of its modulo.

        Arguments:
        - modulo: (mandatory) an string representation of a polynomial
          (like 'x^4+1').
        - coefficients_class: (mandatory) an object resultant from the
          BinaryExtensionModulo build.
        - variable: by default is 'x' and it is only used for the output
          strings representing the polynomials. Must be different than the
          used for the coefficients class.
        - loglevel: by default info, based on the superclass Logger
        enumeration.

        Example:
        >>> import Polynomials
        >>> field = Polynomials.BinaryExtensionModulo('z^8+z^4+z^3+z+1')
        >>> polynomialRing = Polynomials.PolynomialRingModulo('x^4+1',field)
    '''
    if len(variable) != 1:
        raise NameError("The indeterminate must be a single character.")
    if ord('a') > variable.lower() > ord('z'):
        raise NameError("The indeterminate must be a valid alphabet letter.")
    if coefficients_class(0).variable == variable:
        raise NameError("The indeterminate must be different that the "
                        "coefficients class")
    if type(modulo) == str and modulo.count(variable) == 0:
        raise Exception("modulo %s is not defined over %s variable"
                        % (modulo, variable))

    class PolynomialRingModuloConstructor(_Logger):
        '''
            Once have the builder of elements it can be used to generate
            objects that represents and have operations defined. The allow
            representations is a list of elements in the coefficient class
            (other representation would be added in the future) or a string
            representation with polynomial notation.

            Argument:
            - value: (mandatory) string representation of the polynomial or
                     the list of coefficients with Less Significant Coefficient
                     First (the position 0 in the list corresponds with
                     coefficient with zero degree).

            Example:
            >>> import Polynomials
            >>> field = Polynomials.BinaryExtensionModulo('z^8+z^4+z^3+z+1')
            >>> polynomialRing = Polynomials.PolynomialRingModulo('x^4+1',
                                                                  field)
            >>> polynomialRing([field(1),field(6),field(9),field(3)])
            (z+1)*x^3+(z^3+1)*x^2+(z^2+z)*x+1 (mod x^4+1)
        '''
        # This help is shown when, from the last one
        # >>> field?
        # TODOs summary:
        # - isInvertible()
        # - refactoring interpreter methods
        def __init__(self, value, *args, **kwargs):
            super(PolynomialRingModuloConstructor,
                  self).__init__(*args, **kwargs)
            self._coefficientClass = coefficients_class
            self._variable = variable
            self._coefficients = self.__interpretCoefficients(value)
            self._modulo = self.__interpretCoefficients(modulo)
            self.reduce()
            self._gcd = None
            self._multinv = None
            self._hammingWeights = None

        def reduce(self):
            if self.degree >= self.modulodegree:
                q, r = self.__divideBy__(self.coefficients, self._modulo)
                self._gr_coefficients = self.__coefficientsDegree(r)
                self._debug_stream("Reduction of %s (%d) is %s (%d)"
                                   % (self._coefficients, self.degree,
                                      r, self._gr_coefficients))
                self._coefficients = r

        def __str__(self):
            '''
                Readable representation. (%s)
            '''
            return self.__interpretToStr__(self._coefficients)

        def __repr__(self):
            '''
                Unambiguous representation. (%r)
            '''
            return "%s (mod %s)"\
                   % (self.__interpretToStr__(self._coefficients),
                      self.__interpretToStr__(self._modulo))

        def __hex__(self):
            '''
                String where the coefficients are compacted on an hexadecimal
                representation.
            '''
            return self.__interpretToStr__(self._coefficients,
                                           hexSubfield=True)

        def __interpretCoefficients(self, value):
            if type(value) == PolynomialRingModuloConstructor or \
               value.__class__ == PolynomialRingModuloConstructor:
                return value.coefficients
            elif type(value) == list:
                if len(value) == 0:
                    return [self._coefficientClass(0)]
                if all([type(coefficient) == int for coefficient in value]):
                    for i in range(len(value)):
                        value[i] = self._coefficientClass(value[i])
                elif all([str(type(coefficient)).
                          count('BinaryExtensionModuloConstructor')
                          for coefficient in value]):
                    for coefficient in value[:-1]:
                        if value[-1].modulo != coefficient.modulo:
                            raise AssertionError("All the coefficients shall "
                                                 "be from the same field.")
                else:
                    try:
                        for i in range(len(value)):
                            value[i] = self._coefficientClass(int(value[i]))
                    except:
                        raise AssertionError("The given coefficient type '%s'"
                                             "is not an expected '%s'"
                                             % (type(value[i]),
                                                self._coefficientClass))
                return value
            elif type(value) == str:
                return self.__interpretFromStr__(value)
            # TODO: are there other representations
            #       that a constructor can support?
            else:
                raise AssertionError("The given coefficients type '%s'"
                                     "is not interpretable" % (type(value)))

        def __interpretToStr__(self, polynomial, hexSubfield=False):
            if polynomial == 0:
                return '0'  # FIXME: the neutral element of the first operation
            else:
                terms = []  # coefficients representations list
                for idx, coefficient in enumerate(polynomial):
                    exponent = idx
                    # FIXME: those nested 'ifs' can be simplified
                    if exponent == 0:
                        if coefficient == self._coefficientClass(0):
                            terms.append("")
                        elif coefficient == self._coefficientClass(1):
                            terms.append("+1")
                        else:
                            if hexSubfield:
                                terms.append("+0x%X"
                                             % (coefficient.coefficients))
                            else:
                                terms.append("+(%s)" % (coefficient))
                    elif exponent == 1:
                        if coefficient == self._coefficientClass(0):
                            terms.append("")
                        elif coefficient == self._coefficientClass(1):
                            terms.append("+%s" % (self._variable))
                        else:
                            if hexSubfield:
                                terms.append("+0x%X%s"
                                             % (coefficient.coefficients,
                                                self._variable))
                            else:
                                terms.append("+(%s)*%s"
                                             % (coefficient, self._variable))
                    else:
                        if coefficient == self._coefficientClass(0):
                            terms.append("")
                        elif coefficient == self._coefficientClass(1):
                            terms.append("+%s^%d" % (self._variable, exponent))
                        else:
                            if hexSubfield:
                                terms.append("+0x%X%s^%d"
                                             % (coefficient.coefficients,
                                                self._variable, exponent))
                            else:
                                terms.append("+(%s)*%s^%d"
                                             % (coefficient, self._variable,
                                                exponent))
                terms.reverse()
                collect = ''.join(["%s" % (term) for term in terms])
                if len(collect) == 0:
                    return '0'  # neutral of the first operation
                if collect[0] == '+':
                    collect = collect[1:]
                return collect

        def __interpretFromStr__(self, string):
            # FIXME: simplify, that's too big for the task to do.
            string = string.replace(' ','')
            terms = {}
            i = 0
            self._trace_stream("Received the string %r (%d) to interpret"
                               % (string, len(string)))
            while i < len(string):
                self._trace_stream("To be process: %r" % (string[i:]))
#                 while string[i] == ' ' or i == len(string):
#                     i += 1  # ignore any &nbsp;
                # Coefficient area ----
                if string[i] == '(':
                    closer = string.find(')', i)
                    coefficient = string[i+1:closer]
                    self._trace_stream("Found a coefficient %r"
                                       % (coefficient))
                    if closer+1 < len(string):
                        if string[closer+1] == '*':
                            self._trace_stream("'*' sign found.")
                            closer += 2
                        else:
                            close += 1
                    i = closer
                elif string[i:i+2] == '0x':
                    vblePos = string.find(self._variable, i)
                    coefficient = string[i:vblePos]
                    self._trace_stream("Found a coefficient in hexadecimal %r"
                                       % (coefficient))
                    i = vblePos
                else:
                    self._trace_stream("No coefficient specified, "
                                       "it would mean '1'")
                    coefficient = '1'
                # variable area ----
                if string[i] != self._variable:
                    self._trace_stream("Variable not found %s != %r"
                                       % (self._variable, string[i]))
                    # perhaps is the latest coefficient, with x^0 not present, 
                    # and no brackets are containing it. Like sage does.
                    candidate = string[i:]
                    self._trace_stream("coefficient candidate: %r" % candidate)
                    try:
                        self._coefficientClass(candidate)
                    except:  # not the case, continues like this hasn't tried
                        self._trace_stream("It cannot be interpreted "
                                           "as a coefficient")
                        i += 1
                    else:  # That's the case of the previous comment
                        self._trace_stream("It has been the case!")
                        coefficient = candidate
                        i = len(string)
                # exponent area ----
                if i == len(string):
                    terms[0] = coefficient
                    self._trace_stream("Parsing finish! final terms dict: %s"
                                       % (terms))
                    break
                if string[i] == self._variable:
                    j = i+1
                    while string[j] == ' ' or i == len(string):
                        j += 1  # ignore any &nbsp;
                    if string[j] == '^':
                        closer = string.find('+', j)
                        exponent = int(string[j+1:closer])
                        self._trace_stream("Found an exponent %d"
                                           % (exponent))
                        i = closer
                    elif string[j] == '+':
                        exponent = 1
                        self._trace_stream("No exponent means degree '1'")
                        i = j
                elif string[i] == '+':
                    self._trace_stream("No variable means exponent '0'")
                    exponent = 0
                    i += 1
                else:
                    raise SyntaxError("Cannot understand %s as a polynomial "
                                      "ring with coefficients in a binary "
                                      "polynomial field" % (string))
                terms[exponent] = coefficient
                self._trace_stream("Current terms dict: %s" % terms)
                i += 1
                self._trace_stream("i = %d" % (i))
            degrees = terms.keys()
            degrees.sort()
            degree = degrees[-1]
            coefficients = []
            for i in range(degree+1):
                if i in terms:
                    self._trace_stream("processing degree %d term %s"
                                       % (i, terms[i]))
                    coefficients.append(self._coefficientClass(terms[i]))
                else:
                    self._trace_stream("processing degree %d without term"
                                       % (i))
                    coefficients.append(self._coefficientClass(0))
            return coefficients

        @property
        def coefficients(self):
            # return a copy, not the same list
            return self.__normalizePolynomial__(self._coefficients)[:]

        @property
        def expandedCoefficients(self):
            coefficients = self._coefficients[:]
            zerosNeeded = self.modulodegree-len(coefficients)
            coefficients += [self._coefficientClass(0)]*zerosNeeded
            return coefficients

        def __normalizePolynomial__(self, v):
            zero = self._coefficientClass(0)
            while len(v) > 1 and v[-1] == zero:
                # Remember is little endian: the most significant coefficient
                # is one in the highest position of the list
                removed = v.pop()
            return v

        @property
        def modulo(self):
            return self.__interpretToStr__(self._modulo)

        @property
        def degree(self):
            if not hasattr(self, "_gr_coefficients"):
                self._gr_coefficients = \
                    self.__coefficientsDegree(self._coefficients)
                # self._debug_stream("Coefficients %s degree %s"
                #                    % (self._coefficients,
                #                       self._gr_coefficients))
            return self._gr_coefficients

        @property
        def hammingWeight(self):
            """Get the hamming weight of the polynomial.
               Hamming weight is defined as the number of non null elements. In
               the binary case, the number of ones.
            """
            if self._hammingWeights is None:
                self._hammingWeights = [coefficient.hammingWeight\
                                        for coefficient in self._coefficients]
            return sum(self._hammingWeights)

        @property
        def modulodegree(self):
            if not hasattr(self, "_gr_modulo"):
                self._gr_modulo = self.__coefficientsDegree(self._modulo)
            return self._gr_modulo

        def __coefficientsDegree(self, coeffList):
            degree = len(coeffList)-1
            while degree > 0:
                if coeffList[degree] != self._coefficientClass(0):
                    break
                degree -= 1
            return degree

        @property
        def isZero(self):
            '''Neutral element of the first operation, addition.'''
            for coefficient in self.coefficients:
                if coefficient != self._coefficientClass(0):
                    return False
                    # FIXME: would be good to make it time constant
                    #        because its for cryptography.
            return True

        def __zero(self):
            zero = [self._coefficientClass(0)]*self.modulodegree
            return PolynomialRingModuloConstructor(zero,
                                                   loglevel=self.logLevel)

        @property
        def isOne(self):
            '''Neutral element of the second operation, product.'''
            for degree, coefficient in enumerate(self.coefficients):
                search = 1 if degree == 0 else 0
                if coefficient != self._coefficientClass(search):
                    return False
                # FIXME: would be good to make it time constant
                #        because its for cryptography.
            return True

        def __one(self):
            zeros = [self._coefficientClass(0)]*(self.modulodegree-1)
            one = [self._coefficientClass(1)] + zeros
            return PolynomialRingModuloConstructor(one, loglevel=self.logLevel)

#         @property
#         def isInvertible(self):
#             '''Show if the element is invertible modulo for the product
#                operation.
#             '''
#             if self._gcd is None:
#                 self._gcd, _, self._multinv = \
#                     self.__egcd__(self._modulo, self.coefficients)
#             if self._gcd == 1:
#                 return True
#             return False

        def __iter__(self):
            return iter(self.coefficients)

        def iter(self):
            return self.__iter__()

        def __getitem__(self, n):
            if n < len(self.coefficients):
                return self.coefficients[n]
            raise OverflowError("No coefficient with this degree")

        def __type__(self):
            return self.__class__

        def __eq__(self, other):  # => a == b
            # FIXME: would be good to make it time constant
            #        because its for cryptography.
            if other is None:
                return False
            if len(self.coefficients) != len(other.coefficients):
                self._trace_stream("In == operator Different lengths! %d != %d"
                                   % (len(self.coefficients),
                                      len(other.coefficients)))
                return False
            for i, xi in enumerate(self.coefficients):
                if i >= len(other.coefficients):
                    self._error_stream("In == operator Ups, "
                                       "this should not happen")
                    return False
                if xi != other.coefficients[i]:
                    self._debug_stream("In == operator %dth different: "
                                       "%s != %s" % (i, xi,
                                                     other.coefficients[i]))
                    return False
            return True

        def is_(self, other):  # => a == b
            return self == other

        def __ne__(self, other):  # => a!=b
            if self.__eq__(other):
                return False
            return True

        def is_not(self, other):  # => a != b
            return self != other

        # #Operations ----
        # + Addition: ----
        def __add__(self, other):  # => a+b
            result = self.__addition__(self.coefficients, other.coefficients)
            return PolynomialRingModuloConstructor(result,
                                                   loglevel=self.logLevel)

        def __iadd__(self, other):  # => a+=b
            result = self.__addition__(self.coefficients, other.coefficients)
            return PolynomialRingModuloConstructor(result,
                                                   loglevel=self.logLevel)

        def __addition__(self, addend1, addend2):
            size = max(self.modulodegree, len(remainded))
            size = max(size, len(substractor))
            result = [self._coefficientClass(0)]*size
            addend1 = addend1 +\
                [self._coefficientClass(0)]*(size-len(addend1))
            addend2 = addend2 +\
                [self._coefficientClass(0)]*(size-len(addend2))
            for i in range(size):
                result[i] = addend1[i] + addend2[i]
            result = self.__normalizePolynomial__(result)
            return result

        def __sub__(self, other):  # => a-b
            result = self.__substraction__(self.coefficients,
                                           other.coefficients)
            return PolynomialRingModuloConstructor(result,
                                                   loglevel=self.logLevel)

        def __isub__(self, other):  # => a-=b
            result = self.__substraction__(self.coefficients,
                                           other.coefficients)
            return PolynomialRingModuloConstructor(result,
                                                   loglevel=self.logLevel)

        def __substraction__(self, remainded, substractor):
            size = max(self.modulodegree, len(remainded))
            size = max(size, len(substractor))
            result = [self._coefficientClass(0)]*size
            remainded = remainded +\
                [self._coefficientClass(0)]*(size-len(remainded))
            substractor = substractor +\
                [self._coefficientClass(0)] * (size-len(substractor))
            for i in range(size):
                result[i] = remainded[i] - substractor[i]
            result = self.__normalizePolynomial__(result)
            return result

        # * Product ----
        # TODO: __rmul__() for something like a scalar product (n * Polynomial)
        def __mul__(self, other):  # => a*b
            '''Given two polynomials ring elements with coefficients in a
               binary polynomial field, calculate their product.
               Input: Two polynomial ring elements with coefficients in the
                      same binary polynomial ring.
               Output: The product between the two input pylinomials
            '''
            a = self.coefficients
            b = other.coefficients
            self._debug_stream("a * b, where:\n\ta = %s\n\tb = %s"
                               % (self.__interpretToStr__(a),
                                  self.__interpretToStr__(b)))
            res = self.__multiply__(a, b)
            p = PolynomialRingModuloConstructor(res, loglevel=self.logLevel)
            self._debug_stream("c = %s" % (p))
            return p

        def __imul__(self, other):  # => a*=b
            bar = self * other
            return PolynomialRingModuloConstructor(bar.coefficients,
                                                   loglevel=self.logLevel)

        def __multiply__(self, multiplicand, multiplier):
            '''Given two polynomials, proceed with a polynomial product
               (without reduction).
               Input: <coefficients list> multiplicand
                      <coefficients list> multiplier
               Output: <coefficients list> result
            '''
            size = max(self.modulodegree*2, len(multiplicand)*2)
            size = max(size, len(multiplier)*2)
            result = [self._coefficientClass(0)]*size
            self._debug_stream("multiplicand: %s" % multiplicand)
            self._debug_stream("multiplier: %s" % multiplier)
            for i, coefficient in enumerate(multiplier):
                partial = self.__multiplicationStep__(multiplicand,
                                                      coefficient, i)
                for j in range(len(partial)):
                    result[j] += partial[j]
            result = self.__normalizePolynomial__(result)
            self._debug_stream("Result: %s" % result)
            return result

        def __multiplicationStep__(self, multiplicant, coefficient, degree):
            '''Constant time function to calculate one of the steps in the
               multiplication.
               Input: <coefficients list> multiplicant
                      <coefficient> coefficient as binary polynomial element
                      <integer> degree (the exponent where the coefficient is)
               Output: <coefficients list> product line
            '''
            line = [self._coefficientClass(0)]*(len(multiplicant)+degree)
            for i in range(len(multiplicant)):
                # shift: i+ degree
                line[i+degree] = multiplicant[i] * coefficient
            line = self.__normalizePolynomial__(line)
            return line

        # /% Division: ----
        def __div__(self, other):  # => a/b
            q, r = self.__divideBy__(self.coefficients, other.coefficients)
            self._debug_stream("q = %s" % q)
            return PolynomialRingModuloConstructor(q, loglevel=self.logLevel)

        def __idiv__(self, other):  # => a/=b
            q, r = self.__divideBy__(self.coefficients, other.coefficients)
            return PolynomialRingModuloConstructor(q, loglevel=self.logLevel)

        def __mod__(self, other):  # => a%b
            q, r = self.__divideBy__(self.coefficients, other.coefficients)
            return PolynomialRingModuloConstructor(r, loglevel=self.logLevel)

        def _imod__(self, other):  # => a%=b
            q, r = self.__divideBy__(self.coefficients, other.coefficients)
            return PolynomialRingModuloConstructor(r, loglevel=self.logLevel)

        def __divideBy__(self, numerator, denominator):
            zero = self._coefficientClass(0)
            a = self.__normalizePolynomial__(numerator)
            b = self.__normalizePolynomial__(denominator)
            # with this, dividend and divisor are lists
            # where the index in the table of each of the coefficients
            # say the corresponding degree.
            if b == [self._coefficientClass(0)]:
                raise ZeroDivisionError
            gr_a = len(a)-1
            gr_b = len(b)-1
            self._debug_stream("Dividing\n\ta: %s (gr_a = %d) "
                               "\n\tb = %s (gr_b = %d)" % (a, gr_a, b, gr_b))
            if gr_a < gr_b:
                return a, b  # dividend smaller than the divisor
            quotient = []  # it will stack and no need to reverse.
            while gr_a >= gr_b:
                q, r = self.__divisionStep__(a, gr_a, b, gr_b)
                self._debug_stream("Give [%s] / [%s] =\n\tq = %s,\n\tr = [%s]"
                                   % ("".join(" %s," % e for e in a)[1:-1],
                                      "".join(" %s," % e for e in b)[1:-1], q,
                                      "".join(" %s," % e for e in r)[1:-1]))
                quotient.append(q)
                if len(r)-1 < gr_b:
                    break
                while len(r) > 0 and r[-1] == zero:
                    quotient.append(zero)
                    r.pop()
                a = r
                gr_a = len(a)-1
            quotient.reverse()
            if len(r) == 0:
                r = [zero]
            self._debug_stream("Finally = %s * %s/b" % (quotient, r))
            return quotient, r

        # FIXME ---
        # two loops inside the division step! This shall be improved!
        def __divisionStep__(self, a, gr_a, b, gr_b):
            zero = self._coefficientClass(0)
            # 1.- quotient
            q = a[-1]*~b[-1]
            self._debug_stream("Quotient step: a[%d]/b[%d] = %s / %s = "
                               "%s * %s = %s"
                               % (gr_a, gr_b, a[-1], b[-1], a[-1], ~b[-1], q))
            gr_q = gr_a-gr_b
            toSubstract = [zero]*gr_q
            for b_i in b:
                toSubstract.append(b_i*q)
            remainder = []
            for i in range(len(toSubstract)):
                remainder.append(a[i]-toSubstract[i])
            if remainder[-1] == zero:
                remainder.pop()
            return q, remainder

        # ~ Multiplicative inverse: ----
        # - operator.__inv__(a) => ~a
        def __invert__(self):  # => ~a, that means like a^-1
            res = self.__multiplicativeInverse__()
            return PolynomialRingModuloConstructor(res)

        def __multiplicativeInverse__(self):
            '''Multiplicative inverse based on ...
               Input: <coefficients list> a (polynomial to invert)
                      <coefficients list> m (modulo)
               Output: <integer> a^-1: a*a^-1 = 1 (mod m)
               "coefficients list" means "little endian list of coefficients"
               This it the first of the two transformations for the SBoxes
               in the subBytes operation, the one called called g.
            '''
            self._debug_stream("__multiplicativeInverse__: %s"
                               % self.coefficients)
            if self._coefficients == 0:  # FIXME: is this true?
                return self
            if self._gcd is None:
                gcd, _, multinv = \
                    self.__egcd__(self._modulo, self._coefficients)
                self._gcd = PolynomialRingModuloConstructor(gcd)
                self._multinv = PolynomialRingModuloConstructor(multinv)
            self._debug_stream("gcd = %s" % self._gcd)
            self._debug_stream("x = %s" % self._multinv)
            if self._gcd != self.__one():
                bar = self.__interpretToStr__(self._coefficients)
                foo = self.__interpretToStr__(self._modulo)
                raise ArithmeticError("The inverse of %s modulo %s "
                                      "doens't exist! (gcd = %s = %s, "
                                      "candidate = %s = %s)"
                                      % (bar, foo, self._gcd, hex(self._gcd),
                                         self._multinv, hex(self._multinv)))
            else:
                return self._multinv  # % self._modulo

        def __gcd__(self, other):
            a = self.coefficients
            b = other.coefficients
            gcd, _, _ = self.__egcd__(a, b)
            return PolynomialRingModuloConstructor(gcd)

        def __egcd__(self, a, b):
            '''Extended Euclidean gcd (Greatest Common Divisor) Algorithm
               Based on the Sage code (7.2) that has GPLv2+ license:
               sage/rings/ring.pyx:_gcd_univariate_polynomial:2222
               Input: <coefficients list> a
                      <coefficients list> b
               Output: <coefficients list> gcd
                       <coefficients list> u
                       <coefficients list> v
               "coefficients list" means "little endian list of coefficients"
               The binary polynomials u, v are for the B\'ezout's identity:
               $u(x)$, $v(x)$ such that $a(x)\times u(x)+b(x)\times v(x)=g(x)$
            '''
            # --- logging methods
            logInHexa = True

            def doPrint(msg):
                self._debug_stream(msg)

            def getStr(p):
                return self.__interpretToStr__(p, hexSubfield=logInHexa)

            def printAsStr(pName, pValue, tabs=0):
                pStr = getStr(pValue)
                doPrint("%s%s = %s" % ("\t"*tabs, pName, pStr))

            def printAsStrings(pairs, tabs=0):
                for name, value in pairs:
                    printAsStr(name, value, tabs)

            def printQuotient(x, q, y, r, tabs=0):
                xStr = getStr(x)
                qStr = getStr(q)
                yStr = getStr(y)
                rStr = getStr(r)
                doPrint("%s%s = %s * %s + %s" % ("\t"*tabs, xStr, qStr, yStr,
                                                 rStr))
            # --- operation methods
            leading_coefficient = lambda x: x[-1]
            # this lambda simply means get the highest degree coefficient
            sub = self.__substraction__
            mul = self.__multiply__
            div_mod = self.__divideBy__
            # --- The algorithm itself
            zero = [self._coefficientClass(0)]
            a = self.__normalizePolynomial__(a)
            b = self.__normalizePolynomial__(b)
            printAsStrings([["a", a], ["b", b]])
            if b == zero:
                if a == zero:
                    return (zero, zero, zero)
                c = ~leading_coefficient(a)
                d, u, v = self.__multiply__(c, a), [c], zero
            elif a == zero:
                c = ~leading_coefficient(b)
                d, u, v = self.__multiply__(c, b), zero, [c]
            else:
                (u, d, v1, v3) = ([self._coefficientClass(1)], a, zero, b)
                printAsStrings([["u", u], ["d", d], ["v1", v1], ["v3", v3]], 1)
                i = 1
                while v3 != zero:
                    doPrint("\tIteration %d" % i)
                    q, r = div_mod(d, v3)
                    printQuotient(d, q, v3, r, 2)
                    (u, d, v1, v3) = (v1, v3, sub(u, mul(v1, q)), r)
                    printAsStrings([["u", u], ["d", d], ["v1", v1],
                                    ["v3", v3]], 2)
                    i += 1
                v, _ = div_mod(sub(d, mul(a, u)), b)
                printAsStr("v", v, 1)
                if d != zero:
                    doPrint("d != zero")
                    c = ~leading_coefficient(d)
                    d, u, v = mul([c], d), mul([c], u), mul([c], v)
                printAsStrings([["d", d], ["u", u], ["v", v]], 1)
            return d, u, v

        # <<>> Shifts ----
        def __lshift__(self, n):  # => a << n
            shifted = \
                PolynomialRingModuloConstructor(self.coefficients +
                                                [self._coefficientClass(0)]*n,
                                                loglevel=self.logLevel)
            self._debug_stream("%s << %d = %s" % (self, n, shifted))
            return shifted

        def __rshift__(self, n):  # => a >> n
            shifted = \
                PolynomialRingModuloConstructor(self.coefficients
                                                [:len(self.coefficients)-n],
                                                loglevel=self.logLevel)
            self._debug_stream("%s >> %d = %s" % (self, n, shifted))
            return shifted

        def __ilshift__(self, n):  # => <<=
            shifted = \
                PolynomialRingModuloConstructor(self.coefficients +
                                                [self._coefficientClass(0)]*n,
                                                loglevel=self.logLevel)
            self._debug_stream("%s <<= %d = %s" % (self, n, shifted))
            return shifted

        def __irshift__(self, n):  # => >>=
            shifted = \
                PolynomialRingModuloConstructor(self.coefficients
                                                [:len(self.coefficients)-n],
                                                loglevel=self.logLevel)
            self._debug_stream("%s >>= %d = %s" % (self, n, shifted))
            return shifted

        def _cyclic_lshift_(self, n):
            shifted = \
                PolynomialRingModuloConstructor(self._coefficients[n:] +
                                                self._coefficients[:n],
                                                loglevel=self.logLevel)
            self._debug_stream("%s <<> %d = %s" % (self, n, shifted))
            return shifted

        def _cyclic_rshift_(self, n):
            l = len(self._coefficients)
            shifted = \
                PolynomialRingModuloConstructor(self._coefficients[l-n:] +
                                                self._coefficients[:l-n],
                                                loglevel=self.logLevel)
            self._debug_stream("%s <>> %d = %s" % (self, n, shifted))
            return shifted
        # End class PolynomialRingModuloConstructor ----
    return PolynomialRingModuloConstructor


class PolynomialRing(_Logger):
    '''This represents a polynomial over (GF(2^n))^l, with a modulo polynomial
       composed (decomposable in roots) this becomes a algebraic ring.
       The coefficients on this polynomial ring are elements of a polynomial
       field.
    '''
    def __init__(self, nRows, nColumns, wordSize, *args, **kwargs):
        super(PolynomialRing, self).__init__(*args, **kwargs)
        self.__nRows = nRows
        self.__nColumns = nColumns
        field_modulo = getBinaryExtensionFieldModulo(wordSize)
        self._field = BinaryExtensionModulo(field_modulo)

    def product(self, ax, sx):
        '''Given two polynomials over F_{2^8} multiplie them modulo x^{4}+1
           s'(x) = a(x) \otimes s(x)
           [s'_0,c]   [a_3 a_0 a_1 a_2] [s_0,c]
           [s'_1,c] = [a_2 a_3 a_0 a_1] [s_1,c]
           [s'_2,c]   [a_1 a_2 a_3 a_0] [s_2,c]
           [s'_3,c]   [a_0 a_1 a_2 a_3] [s_3,c]
           s'_0,c = (a_3 \bullet s_0,c) \oplus (a_0 \bullet s_1,c) \oplus
                    (a_1 \bullet s_2,c) \oplus (a_2 \bullet s_3,c)
           s'_1,c = (a_2 \bullet s_0,c) \oplus (a_3 \bullet s_1,c) \oplus
                    (a_0 \bullet s_2,c) \oplus (a_1 \bullet s_3,c)
           s'_2,c = (a_1 \bullet s_0,c) \oplus (a_2 \bullet s_1,c) \oplus
                    (a_3 \bullet s_2,c) \oplus (a_0 \bullet s_3,c)
           s'_3,c = (a_0 \bullet s_0,c) \oplus (a_1 \bullet s_1,c) \oplus
                    (a_2 \bullet s_2,c) \oplus (a_3 \bullet s_3,c)
           Where \bullet is the finite field (F_{2^8}) multiplication,
           and \oplus an xor operation
           Input:
           Output:
        '''
        res = _deepcopy(sx)  # FIXME: #[[0]*self.__nRows]*self.__nColumns ----
        for c in range(self.__nColumns):
            shifted_ax = _shift(ax, self.__nRows-1)
            for r in range(self.__nRows):
                res[r][c] = 0
                for rbis in range(self.__nRows):
                    a = self._field(shifted_ax[rbis])
                    b = self._field(sx[rbis][c])
                    res[r][c] ^= (a*b)._coefficients
                shifted_ax = _shift(shifted_ax, -1)
        return res


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
