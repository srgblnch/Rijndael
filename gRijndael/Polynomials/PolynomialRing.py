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
from ..Logger import Logger as _Logger
from ..Logger import XORctr as _XORctr
from ..ThirdLevel import shift as _shift
from .BinaryPolynomials import *


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
    if version_info.major == 2:
        variablecode = variable.lower()
    elif version_info.major == 3:
        variablecode = ord(variable.lower())
    if ord('a') > variablecode  > ord('z'):
        raise NameError("The indeterminate must be a valid alphabet letter.")
    if coefficients_class(0).variable == variable:
        raise NameError("The indeterminate must be different that the "
                        "coefficients class")
    if type(modulo) == str and modulo.count(variable) == 0:
        raise Exception("modulo %s is not defined over %s variable"
                        % (modulo, variable))

    class PolynomialRingModuloConstructor(_Logger, _XORctr):
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
            self.includeInstance(self._coefficients)
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

        def __int__(self):
            '''
                Generate a integer representing the polynomial
            '''
            value = 0
            for degree, coefficient in enumerate(self.coefficients):
                value += coefficient.coefficients <<\
                    (degree * (coefficient.modulodegree-1))
            return value

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
            string = string.replace(' ', '')
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
                    vblePos = string.find(self._variable, i+2)
                    addPos = string.find('+', i+2)
                    if vblePos == -1:  # if there is no vbles
                        if addPos == -1:  # if there is no mode monomials
                            coefficient = string[i:]
                            i = len(string)  # point to the end
                        else:
                            coefficient = string[i:addPos]
                            i = addPos
                    else:
                        coefficient = string[i:vblePos]
                        i = vblePos
                    self._trace_stream("Found a coefficient in hexadecimal %r"
                                       % (coefficient))
                    coefficient = int(coefficient, 16)
                else:
                    self._trace_stream("No coefficient specified, "
                                       "it would mean '1'")
                    coefficient = '1'
                # variable area ----
                if i == len(string):
                    terms[0] = coefficient
                    self._trace_stream("Parsing finish! final terms dict: %s"
                                       % (terms))
                    break
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
            degrees = list(terms.keys())
            degrees.sort()
            degree = degrees[-1]
            coefficients = []
            for i in range(degree+1):
                if i in terms:
                    self._trace_stream("Processing degree %d term %s"
                                       % (i, terms[i]))
                    coefficients.append(self._coefficientClass(terms[i]))
                else:
                    self._trace_stream("Processing degree %d without term"
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
            return sum(self.hammingWeightPerCoefficient)

        @property
        def hammingWeightPerCoefficient(self):
            if self._hammingWeights is None:
                self._hammingWeights = [coefficient.hammingWeight
                                        for coefficient in self._coefficients]
            return self._hammingWeights[:]

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

        @property
        def isInvertible(self):
            '''Show if the element is invertible modulo for the product
               operation.
            '''
            if self._gcd is None or self._multinv is None:
                self._gcd, _, self._multinv = \
                    self.__egcd__(self._modulo, self.coefficients)
            if self._gcd == [self._coefficientClass(1)]:
                return True
            print("...")
            return False

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
            size = max(self.modulodegree, len(addend1))
            size = max(size, len(addend2))
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
            if self._multinv is None:
                self._multinv = self.__multiplicativeInverse__()
            return PolynomialRingModuloConstructor(self._multinv)

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
            if self._gcd is None or self._multinv is None:
                self._gcd, _, self._multinv = \
                    self.__egcd__(self._modulo, self._coefficients)
            gcd = PolynomialRingModuloConstructor(self._gcd)
            multinv = PolynomialRingModuloConstructor(self._multinv)
            self._debug_stream("gcd = %s" % gcd)
            self._debug_stream("multiplicative inverse = %s" % multinv)
            if gcd != self.__one():
                bar = self.__interpretToStr__(self._coefficients)
                foo = self.__interpretToStr__(self._modulo)
                raise ArithmeticError("The inverse of %s modulo %s "
                                      "doens't exist! (gcd = %s = %s, "
                                      "candidate = %s = %s)"
                                      % (bar, foo, self._gcd, hex(gcd),
                                         self._multinv, hex(multinv)))
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


# class PolynomialRing(_Logger):
#     '''This represents a polynomial over (GF(2^n))^l, with a modulo
#        polynomial composed (decomposable in roots) this becomes a algebraic
#        ring. The coefficients on this polynomial ring are elements of a
#        polynomial field.
#     '''
#     def __init__(self, nRows, nColumns, wordSize, *args, **kwargs):
#         super(PolynomialRing, self).__init__(*args, **kwargs)
#         self.__nRows = nRows
#         self.__nColumns = nColumns
#         field_modulo = getBinaryExtensionFieldModulo(wordSize)
#         self._field = BinaryExtensionModulo(field_modulo)
# #
#     def product(self, ax, sx):
#         '''Given two polynomials over F_{2^8} multiply them modulo x^{4}+1
#            s'(x) = a(x) \otimes s(x)
#            [s'_0,c]   [a_3 a_0 a_1 a_2] [s_0,c]
#            [s'_1,c] = [a_2 a_3 a_0 a_1] [s_1,c]
#            [s'_2,c]   [a_1 a_2 a_3 a_0] [s_2,c]
#            [s'_3,c]   [a_0 a_1 a_2 a_3] [s_3,c]
#            s'_0,c = (a_3 \bullet s_0,c) \oplus (a_0 \bullet s_1,c) \oplus
#                     (a_1 \bullet s_2,c) \oplus (a_2 \bullet s_3,c)
#            s'_1,c = (a_2 \bullet s_0,c) \oplus (a_3 \bullet s_1,c) \oplus
#                     (a_0 \bullet s_2,c) \oplus (a_1 \bullet s_3,c)
#            s'_2,c = (a_1 \bullet s_0,c) \oplus (a_2 \bullet s_1,c) \oplus
#                     (a_3 \bullet s_2,c) \oplus (a_0 \bullet s_3,c)
#            s'_3,c = (a_0 \bullet s_0,c) \oplus (a_1 \bullet s_1,c) \oplus
#                     (a_2 \bullet s_2,c) \oplus (a_3 \bullet s_3,c)
#            Where \bullet is the finite field (F_{2^8}) multiplication,
#            and \oplus an xor operation
#            Input:
#            Output:
#         '''
#         res = _deepcopy(sx)  # FIXME: [[0]*self.__nRows]*self.__nColumns ----
#         self._debug_stream("PolynomialRing.product(%s,%s)" % (ax, sx))
#         for c in range(self.__nColumns):
#             shifted_ax = _shift(ax, self.__nRows-1)
#             for r in range(self.__nRows):
#                 res[r][c] = 0
#                 for rbis in range(self.__nRows):
#                     a = self._field(shifted_ax[rbis])
#                     b = self._field(sx[rbis][c])
#                     res[r][c] ^= (a*b)._coefficients
#                 shifted_ax = _shift(shifted_ax, -1)
#         return res


def getPolynomialRingWithBinaryCoefficients(ringDegree, coefficientsDegree):
    fieldModulo = getBinaryExtensionFieldModulo(coefficientsDegree)
    field = BinaryExtensionModulo(fieldModulo, variable='z')
    ring = PolynomialRingModulo('x^%d+1' % ringDegree, field)
    c_x = {2: {2: '0x3x+0x2',
               3: '0x6x+0x4',
               4: '0x5x+0x6',
               5: '0x5x+0x15',
               6: '0x34x+0x7',
               7: '0x2Cx+0x74',
               8: '0x78x+0xA6',
               9: '0x146x+0xCE',
               10: '0x2D8x+0x2F0',
               11: '0x13Dx+0x343',
               12: '0x2D3x+0x8D6',
               13: '0x99Ex+0x1439',
               14: '0x1E58x+0xDD8',
               15: '0x60DCx+0x2DCC',
               16: '0x318Fx+0x76A8'},
           3: {2: '0x2x^2+0x2x+0x3',
               3: '0x4x^2+0x4x+0x5',
               4: '0x3x^2+0xCx+0x3',
               5: '0x12x^2+0x5x+0x13',
               6: '0x2Cx^2+0x2Ax+0x19',
               7: '0x15x^2+0xFx+0x62',
               8: '0x4Bx^2+0x3Cx+0x33',
               9: '0x6Ax^2+0xC7x+0xB4',
               10: '0xEAx^2+0xE5x+0xE5',
               11: '0x496x^2+0x347x+0x34A',
               12: '0xE70x^2+0x8E6x+0x41F',
               13: '0x1B5x^2+0x1C36x+0x536',
               14: '0x3B21x^2+0x1AE0x+0x2F2C',
               15: '0x2D1Ax^2+0x4D6Cx+0x5A51',
               16: '0xB10Ex^2+0x70B9x+0x57AA'},
           4: {2: '0x2x^2+0x2x+0x3',
               3: '0x3x^3+0x3x^2+0x2x+0x4',
               4: '0x3x^3+0x9x^2+0x3x+0xC',
               5: '0x13x^3+0x9x^2+0xBx+0x9',
               6: '0xDx^3+0x2Cx^2+0x16x+0x34',
               7: '0x63x^3+0x58x^2+0x72x+0x43',
               # the Rijndael's original
               8: '0x3x^3+x^2+x+0x2',  # (z+1)*x^3+x^2+x+(z)',
               # 8: '0xCAx^3+0xB8x^2+0xC9x+0x39',
               9: '0xD5x^3+0x17x^2+0x133x+0x145',
               10: '0x305x^3+0x21Bx^2+0x2D9x+0x1A3',
               11: '0x24Ex^3+0x17Ax^2+0x40Fx+0xF5',
               12: '0x26Dx^3+0x569x^2+0xCC6x+0x41F',
               13: '0xF34x^3+0xD62x^2+0x24Fx+0x1F88',
               14: '0x857x^3+0x12B2x^2+0x29D9x+0x2EAC',
               15: '0x4B89x^3+0x558Ax^2+0x56F0x+0x3D68',
               16: '0x203Fx^3+0xF62Cx^2+0x2D31x+0x9DCC'},
           5: {2: 'x^4+x^3+x^2+0x2x+0x2',
               3: '0x5x^4+0x4x^3+0x3x^2+0x4x+0x4',
               4: '0x3x^4+0x3x^3+0x3x^2+0x3x+0x5',
               5: '0x6x^4+0x11x^3+0x6x^2+0x7x+0x1A',
               6: '0x29x^4+0x31x^3+0x1Ax^2+0x16x+0x2C',
               7: '0x32x^4+0x17x^3+0x43x^2+0x68x+0x47',
               8: '0x33x^4+0x3Cx^3+0x35x^2+0x3Cx+0x3A',
               9: '0x1C9x^4+0x57x^3+0x32x^2+0x9Ex+0x11C',
               10: '0x3A2x^4+0x13Ex^3+0x274x^2+0x243x+0xBC',
               11: '0x433x^4+0x26Ex^3+0x729x^2+0x34Cx+0x354',
               12: '0x2B3x^4+0x5Fx^3+0x698x^2+0x11Fx+0x5F4',
               13: '0xF84x^4+0x10DAx^3+0x1427x^2+0x1AB8x+0x107E',
               14: '0x1D2Ax^4+0xBCEx^3+0x20E3x^2+0x1A51x+0x325D',
               15: '0x548Dx^4+0x3D44x^3+0x16E4x^2+0x388Fx+0x1CF1',
               16: '0x319Fx^4+0x4A1Fx^3+0x8B52x^2+0xD078x+0x1A7E'},
           6: {2: '0x3x^4+x^3+0x2x^2+x+0x2',
               3: '0x6x^4+0x5x^3+0x5x^2+0x6x+0x2',
               4: '0x6x^5+0x9x^4+0x3x^3+0x3x^2+0x3x+0x3',
               5: '0x14x^5+0x11x^4+0xBx^3+0x15x^2+0x11x+0xE',
               6: '0x2Bx^5+0x9x^4+0x1Dx^3+0x23x^2+0x24x+0x2C',
               7: '0x26x^5+0x65x^4+0x50x^3+0x66x^2+0x55x+0x1D',
               8: '0x6Dx^5+0x1Fx^4+0x2Ex^3+0x62x^2+0x62x+0x8D',
               9: '0x1CCx^5+0x1Fx^4+0xCDx^3+0x51x^2+0x9Dx+0x149',
               10: '0x87x^5+0x385x^4+0x332x^3+0x1B9x^2+0x313x+0x263',
               11: '0x4E4x^5+0x625x^4+0x3D2x^3+0x1C5x^2+0x6DAx+0x433',
               12: '0x63Ax^5+0x436x^4+0x296x^3+0xCBCx^2+0x2CFx+0xA9C',
               13: '0x297x^5+0x14D4x^4+0x115Ex^3+0xA33x^2+0x18BAx+0x1674',
               14: '0x12ADx^5+0x12D9x^4+0x2A23x^3+0x4BDx^2+0x22F6x+0x2595',
               15: '0x60EAx^5+0x3079x^4+0x383Ex^3+0x293Ex^2+0x4AC9x+0x1E8E',
               16: '0x7168x^5+0x9DA2x^4+0x66DAx^3+0x394Fx^2+0x3893x+0xFA6'},
           7: {2: '0x3x^4+0x3x^3+0x2x^2+0x2x+1',
               3: '0x4x^5+0x3x^4+0x6x^3+0x6x^2+0x4x+0x5',
               4: '0x3x^6+0x3x^5+0x3x^4+0x3x^3+0x3x^2+0x3x+0x6',
               5: '0x6x^6+0x5x^5+0x5x^4+0x19x^3+0xDx^2+0x5x+0x1A',
               6: '0x2Ex^6+0x32x^5+0x17x^4+0x12x^3+0xDx^2+0x6x+0x1C',
               7: '0x4Cx^6+0x32x^5+0x23x^4+0x3Ex^3+0x64x^2+0x27x+0x4A',
               8: '0x1Fx^6+0x26x^5+0x1Dx^4+0xA6x^3+0x6Cx^2+0xC6x+0xC5',
               9: '0x18Dx^6+0x14Cx^5+0x129x^4+0x17x^3+0x13Ax^2+0x14Dx+0x39',
               10: '0x227x^6+0x115x^5+0x30Fx^4+0x107x^3+0x34Ex^2+0x217x+0x76',
               11: '0x2Fx^6+0xF1x^5+0x756x^4+0x686x^3+0x436x^2+0x77x+0x591',
               12: '0xA7Ax^6+0xE8Ax^5+0x1D9x^4+0x30Bx^3+0x371x^2+0xD91x+0xA2E',
               13: '0x736x^6+0x18CCx^5+0x4C7x^4+0x95Dx^3+0x1D23x^2+0x1D0Cx'
                   '+0x1583',
               14: '0x1D0Ex^6+0x3A2Ex^5+0x3612x^4+0x322Fx^3+0x1F1x^2+0x2935x+'
                   '0x766',
               15: '0x2C99x^6+0x7446x^5+0x23CEx^4+0x2F70x^3+0x245Fx^2+0x486Dx+'
                   '0x352C',
               16: '0x81DEx^6+0x2357x^5+0x225Fx^4+0x7724x^3+0xE9Dx^2+0x6167x+'
                   '0xB295'},
           8: {2: '0x2x^7+x^6+0x2x^5+0x2x^4+0x2x^3+0x2x^2+0x2x+0x2',
               3: '0x3x^6+0x6x^5+0x5x^4+0x3x^3+0x4x^2+0x6x+0x4',
               4: '0x6x^7+0xEx^6+0x5x^5+0x5x^4+0x5x^3+0xEx^2+0x4x+0x8',
               5: '0x8x^7+0x7x^6+0x5x^5+0x1Ax^4+0xCx^3+0x1Ax^2+0x7x+0x13',
               6: '0x2Dx^7+0x16x^6+0xDx^5+0x1Cx^4+0x23x^3+0x1Ax^2+0x11x+0xD',
               7: '0x35x^7+0x66x^6+0x46x^5+0x38x^4+0x4Ex^3+0x47x^2+0x3Cx+0x30',
               8: '0x52x^7+0x74x^6+0xD8x^5+0xFx^4+0xCBx^3+0x6Ax^2+0xCAx+0xC5',
               9: '0x4Ex^7+0x3Dx^6+0xB6x^5+0xCBx^4+0xEAx^3+0x29x^2+0x126x+'
                  '0x133',
               10: '0x28Dx^7+0x2Fx^6+0x265x^5+0x131x^4+0xBDx^3+0x23Cx^2+'
                   '0x329x+0x332',
               11: '0x7E4x^7+0x31Ax^6+0x1ACx^5+0x2ADx^4+0x652x^3+0x5Dx^2+'
                   '0x5Fx+0x1C9',
               12: '0x38Bx^7+0x99Ax^6+0x4CCx^5+0x723x^4+0x15Fx^3+0x45Ax^2+'
                   '0xCC5x+0xF32',
               13: '0x978x^7+0x8B8x^6+0x1BC2x^5+0x1196x^4+0x103Fx^3+0x9E6x^2+'
                   '0x7Fx+0x3DA',
               14: '0x28D7x^7+0xBCEx^6+0x3055x^5+0x206Fx^4+0x16A4x^3+0x437x^2'
                   '+0x1799x+0x3346',
               15: '0x5C0Fx^7+0xA75x^6+0x62CDx^5+0x44DAx^4+0x6A49x^3+0x7C32x^2'
                   '+0xAC7x+0x1F16',
               16: '0x3B16x^7+0x84B7x^6+0x6794x^5+0xC1D3x^4+0xB4Fx^3+0xC157x^2'
                   '+0x879Ax+0x4E87'}
           }[ringDegree][coefficientsDegree]
    return (ring(c_x), ring, field)
