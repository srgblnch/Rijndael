#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: Polynomials.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2014,2015 (copyleft)
##
## This file is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This file is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this file.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

from Logger import Logger as _Logger
#from Logger import levelFromMeaning as _levelFromMeaning
from ThirdLevel import shift as _shift
#from ThirdLevel import binlen as _binlen
from copy import copy as _copy
from copy import deepcopy as _deepcopy

def BinaryPolynomialModulo(modulo,variable='z',loglevel=_Logger._info):
    '''BinaryPolynomialModulo is a builder for the given modulo. The returning
       object can generate elements in this field or ring (depending on the 
       reducibility of the modulo polynomial).
       
       The integer representation will use binary representation to assign the 
       MSB to highest degree and the LSB to the 0 degree. For the string 
       representation the sage notation has been take as inspiration.
       
       Arguments:
       - modulo: (mandatory) an integer or an string representation of a 
         polynomial (like 'z^8+z^4+z^3+z+1' that's equivalent to 0x11B).
       - variable: by default is 'z' and it is only used for the output strings
         representing the polynomials.
       - loglevel: by default info, based on the superclass Logger enumeration.
       
       Example:
       >>> import Polynomials
       >>> field = Polynomials.BinaryPolynomialModulo('z^8+z^4+z^3+z+1')
    '''
    if type(modulo) == str and modulo.count(variable) == 0:
        raise Exception("modulo %s is not defined over %s variable"
                        %(modulo,variable))
    #This help is shown when
    #>>> Polynomials.BinaryPolynomialModulo?
    class BinaryPolynomialModuloConstructor(_Logger):
        def __init__(self,value):
            '''Polynomial defined by an integer or an string representation 
               of an element of the field or ring defined when made the builder
               object.
               
               Argument:
               - value: (mandatory) the value to be interpreted as a binary 
                 polynomial finite field or ring.
                 
               Example:
               >>> from Polynomials import BinaryPolynomialModulo
               >>> field = BinaryPolynomialModulo('z^8+z^4+z^3+z+1')
               >>> a = field(73); a
               z^6+z^3+1 (mod z^8+z^4+z^3+z+1)
            '''
            #This help is shown when, from the last one
            #>>> field?
            #FIXME: improve the logging on this class
            _Logger.__init__(self,loglevel)
            if len(variable) != 1:
                raise NameError("The indeterminate must be "\
                                "a single character.")
            if ord('a') > variable.lower() > ord('z'):
                raise NameError("The indeterminate must be a valid "\
                                "alphabet letter.")
            self._variable = variable
            if type(value) == BinaryPolynomialModuloConstructor or \
               value.__class__ == BinaryPolynomialModuloConstructor:
                self._coefficients = value.coefficients
            elif type(value) == int:
                self._coefficients = abs(value)
            elif type(value) == str:
                self._coefficients = self.__interpretFromStr__(value)
            else:
                try:#Do a last try to interpret the coefficients
                    self._coefficients = int(value)
                except Exception,e:
                    raise AssertionError("The given coefficients type '%s'"\
                                         "is not interpretable"%(type(value)))
            self._gcd = None
            self._multinv = None
            self._debug_stream("coefficients", self._coefficients)
            if type(modulo) == int:
                self._modulo = modulo
            elif type(modulo) == str:
                self._modulo = self.__interpretFromStr__(modulo)
            else:
                try:#Do a last try to interpret the coefficients
                    self._modulo = int(modulo)
                except Exception,e:
                    raise AssertionError("The given modulo type '%s'"\
                                         "is not interpretable"%(type(modulo)))
            self._debug_stream("modulo", self._modulo)
            #if the degree of coefficients > degree of modulo, do the reduction
            if self.degree >= len("{0:b}".format(self._modulo)):
                q,r = self.__division__(self._coefficients,self._modulo)
                self._coefficients = r
                self._debug_stream("reduced coefficients", self._coefficients)
        @property
        def coefficients(self):
            return self._coefficients
        @property
        def modulo(self):
            return self.__interpretToStr__(self._modulo)
        @property
        def variable(self):
            return self._variable
        @property
        def degree(self):
            return len("{0:b}".format(self._coefficients))
        @property
        def hammingWeight(self):
            return bin(self._coefficients).count('1')
        @property
        def modulodegree(self):
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
            if self._gcd == None:
                self._gcd,self._multinv,y = \
                                 self.__egcd__(self._coefficients,self._modulo)
            if self._gcd == 1:
                return True
            return False
        def __iter__(self):
            return iter("{0:b}".format(self._coefficients))
        def iter(self):
            return self.__iter__()
        def __getitem__(self,n):
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
            def comparator(self,other):
                if other.__class__ == type(None):
                    return function(self,other)
                if str(other.__class__) != str(self.__class__):
                    raise EnvironmentError("Cannot compare with non "\
                                           "polynomials (%s,%s)"
                                           %(type(other),other.__class__))
                if not self.variable == other.variable:
                    raise EnvironmentError("Uncompatible polynomials")
                if not self._modulo == other._modulo:
                    raise EnvironmentError("Those polynomials are not in the "\
                                           "same equivalence class")
                return function(self,other)
            return comparator
        def __str__(self):
            '''Readable representation. (%s)
            '''
            return self.__interpretToStr__(self._coefficients)
        def __repr__(self):
            '''Unambiguous representation. (%r)
            '''
            return "%s (mod %s)"%(self.__interpretToStr__(self._coefficients),
                                  self.__interpretToStr__(self._modulo))
        def __bin__(self):
            #TODO: doesn't work, check it
            return bin(self._coefficients)
        def __oct__(self):
            return oct(self._coefficients)
        def __hex__(self):
            return hex(self._coefficients)
        def __interpretToStr__(self,value):
            if value == 0:
                return '0'#FIXME: the neutral element of the first operation
            else:
                terms = [] #coefficients representations list
                bitlist = "{0:b}".format(value)
                #FIXME: Improve this dirtied casuistry... Not efficient.
                for idx,coefficient in enumerate(bitlist):
                    exponent = len(bitlist)-idx-1
                    if coefficient == '0':
                        terms.append('')
                    elif exponent == 0:#and coefficient == '1'
                        terms.append('+1')
                    elif exponent == 1:#and coefficient == '1'
                        #equiv to z^1 but short
                        terms.append('+%s'%(self._variable))
                    else:
                        terms.append('+%s^%d'%(self._variable,exponent))
                collect = ''.join(["%s"%(r) for r in terms])
                if collect[0] == '+':#remove the first sign if present
                    collect = collect[1:]
                return collect
        def __interpretFromStr__(self,string):
            terms = string.strip().split('+')
            value = 0
            for i in range(len(terms)):
                if terms[i] == '%s'%self._variable:
                    value |= 1<<1#z^1
                elif terms[i] == '1':
                    value |= 1
                elif terms[i].count(self._variable):
                    exponent = int(terms[i].split('%s^'%self._variable)[1])
                    value |= 1<<exponent
                else:
                    raise SyntaxError("the term %s cannot be interpreted"
                                      %(terms[i]))
            return value
        def __abs__(self):
            return BinaryPolynomialModuloConstructor(abs(self._coefficients))
        def __len__(self):
            bits = "{0:b}".format(self._coefficients)
            if bits[0] == '-':
                bits = bits[1:]
            return len(bits)
        @checkTypes
        def __eq__(self,other):# => a == b
            if other == None:
                return False
            if self._coefficients == other._coefficients:
                return True
            return False
        @checkTypes
        def is_(self,other):# => a == b
            return self == other
        @checkTypes
        def __ne__(self,other):# => a!=b
            if self.__eq__(other):
                return False
            return True
        @checkTypes
        def is_not(self,other):# => a != b
            return self != other
        #Meaningless operators in polynomials:
        # operator.__lt__(a,b) => a<b
        # operator.__le__(a,b) => a<=b
        # operator.__gt__(a,b) => a>b
        # operator.__ge__(a,b) => a>=b
        #---- #Operations
        #---- + Addition
        @checkTypes
        def __add__(self,other):# => a+b
            a = _copy(self.coefficients)
            b = _copy(other.coefficients)
            return BinaryPolynomialModuloConstructor(a^b)
        def __iadd__(self,other):# => a+=b
            bar = self + other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        def __pos__(self):# => +a
            return self
        #---- - Substraction
        def __neg__(self):# => -a
            return self
        def __sub__(self, other):# => a-b
            bar = -other
            a = _copy(self.coefficients)
            b = _copy(other.coefficients)
            return BinaryPolynomialModuloConstructor(a^b)
        def __isub__(self,other):# => a-=b
            bar = self - other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        #---- * Product
        @checkTypes
        def __mul__(self,other):# => a*b
            '''
            '''
            a = _copy(self._coefficients)
            b = _copy(other._coefficients)
            res = self.__multiply__(a,b)
            self._debug_stream("c = a * b = %s * %s = %s"
                              %(self.__interpretToStr__(a),
                                self.__interpretToStr__(b),
                                self.__interpretToStr__(res)))
            return BinaryPolynomialModuloConstructor(res)
        def __imul__(self,other):# => a*=b
            bar = self * other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        def xtimes(self):
            return self << 1
        def __multiply__(self,a,b):
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
            self._debug_stream("a %s"%self.__interpretToStr__(a))
            self._debug_stream("b %s"%self.__interpretToStr__(b))
            result = 0
            mask = 1
            i = 0
            while mask < self._modulo:
                bit = b & mask
                result = self.__multiplicationStep__(a,bit,i,result)
                mask <<= 1
                i += 1
            return result
        def __multiplicationStep__(self,a,bit,i,accum):
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
                self._debug_stream("aShifted: %s"%
                                 self.__interpretToStr__(aShifted))
                return newerAccum
            else:
                return accum
        def __matrix_product__(self,other):
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
            self._debug_stream("self * other: %r * %r = %s * %s"%(self,other,
                  bin(self._coefficients),bin(other._coefficients)))
            #self._coefficients in binary corresponds to last row
            #1 shift to the left is row0
            row = self._cyclic_rshift_(1)
            res = 0
            self._debug_stream("input: %s %r"%(bin(other._coefficients),other))
            input = self.__mirrorbits__(other._coefficients)
            for i in range(self.modulodegree-1):
                res = res << 1
                self._debug_stream("row[%d]: %s %r"%(i,bin(row._coefficients),row))
                bitProduct = row._coefficients & input
                parity = self.__parity__(bitProduct)
                row = row._cyclic_rshift_(1)
                res |= parity
            self._debug_stream("result: %s"%bin(res))
            return BinaryPolynomialModuloConstructor(self.__mirrorbits__(res))
        def __parity__(self,bits):
            '''Given a number, use a bit representation to proceed with an xor 
               (addition in GF(2)) of each of its elements.
            '''
            msg = "parity = %s"%(bin(bits))
            while bits > 1:
                bits = (bits >> 1) ^ (bits & 1)
            self._debug_stream("%s = %d"%(msg,bits))
            return bits
        def __mirrorbits__(self,bits):
            '''Exchange the bit significance by placing the LSB first and the
               MSB at the end.
            '''
            maxbits = self.modulodegree-1
            origin = bits
            mirror = 0
            for i in range(maxbits):#while bits > 0:
                mirror <<= 1
                mirror |= origin & 1
                origin >>= 1
            self._debug_stream("mirrored %s to %s"%(bin(bits),bin(mirror)))
            return mirror
        #---- /% Division
        def __division__(self,a,b):
            '''TODO
            '''
            #FIXME: check division by 0 => ZeroDivisionError
            self._debug_stream("\n<division>")
            gr_a = len("{0:b}".format(a))-1
            gr_b = len("{0:b}".format(b))-1
            q = 0
            r = a
            self._debug_stream("a",a)
            self._debug_stream("b",b)
            self._debug_stream("q",q)
            self._debug_stream("r",r)
            shift = gr_a-gr_b
            while len("{0:b}".format(r))>=len("{0:b}".format(b)) and \
                  shift >= 0:
                #FIXME: this means deg(r) >= deg(b), but it's horrible
                gr_r = len("{0:b}".format(r))-1
                if shift > 0:
                    temp = int("{0:b}".format(r)[0:-shift],2)<<shift
                else:
                    temp = r
                self._debug_stream("temp",temp)
                subs = b << shift
                self._debug_stream("subs",subs)
                if len("{0:b}".format(temp)) == len("{0:b}".format(subs)):
                    bar = temp ^ subs
                    self._debug_stream("temp ^subs",bar)
                    if shift > 0:
                        mask = int('1'*shift,2)
                        q = q | 1<<(shift)
                        r = bar | (a & mask)
                    else:
                        q |= 1
                        r = bar
                self._debug_stream("q",q)
                self._debug_stream("r",r)
                gr_a -= 1
                shift = gr_a-gr_b
            self._debug_stream("<\\division>\n")
            return (q,r)
        def __div__(self,other):# => a/b
            q,r = self.__division__(self._coefficients,other._coefficients)
            return BinaryPolynomialModuloConstructor(q)
            #FIXME: the constructor will reduce it having the rest 
            #and not the quotient
        def __idiv__(self,other):# => a/=b
            q,r = self.__division__(self._coefficients,other._coefficients)
            return BinaryPolynomialModuloConstructor(q)
        def __mod__(self,other):# => a%b
            q,r = self.__division__(self._coefficients,other._coefficients)
            return BinaryPolynomialModuloConstructor(r)
        def _imod__(self,other):# => a%=b
            q,r = self.__division__(self._coefficients,other._coefficients)
            return BinaryPolynomialModuloConstructor(r)
        #---- ~ Multiplicative inverse 
        #      - operator.__inv__(a) => ~a
        def __egcd__(self,a,b):
            '''Extended Euclidean gcd (Greatest Common Divisor) Algorithm
               From Hankerson,Menezes,Vanstone "Guide to Elliptic Curve 
               Cryptography" Algorithm 2.47.
               Input: <integer> a (polynomial bit representation)
                      <integer> b (polynomial bit representation)
               Output: <integer> gcd
                       <integer> x (polynomial bit representation)
                       <integer> y (polynomial bit representation)
            '''
            u,v = a,b
            self._debug_stream("u",u)
            self._debug_stream("v",v)
            g1,g2,h1,h2 = 1,0,0,1
            self._debug_stream("g1",g1)
            self._debug_stream("g2",g2)
            self._debug_stream("h1",h1)
            self._debug_stream("h2",h2)
            while u != 0:
                j = len("{0:b}".format(u))-len("{0:b}".format(v))
                if j < 0:
                    self._debug_stream("%d < 0"%j)
                    #u <-> v
                    u,v = v,u
                    #g1 <-> g2
                    g1,g2 = g2,g1
                    #h1 <-> h2
                    h1,h2 = h2,h1
                    j = -j
                u = u^(v<<j)
                g1 = g1^(g2<<j)
                h1 = h1^(h2<<j)
                self._debug_stream("\tu",u)
                self._debug_stream("\tg1",g1)
                self._debug_stream("\th1",h1)
            d,g,h = v,g2,h2
            self._debug_stream("d",d)
            self._debug_stream("g",g)
            self._debug_stream("h",h)
            return d,g,h
        @checkTypes
        def __gcd__(self,other):
            a = self._coefficients
            b = other._coefficients
            gcd,x,y = self.__egcd__(a,b)
            return gcd
        def __multiplicativeInverse__(self):
            '''Multiplicative inverse based on ...
               Input: <integer> a (polynomial bit representation)
                      <integer> m (modulo polynomial)
               Output: <integer> a^-1: a*a^-1 = 1 (mod m)
               This it the first of the two transformations for the SBoxes 
               in the subBytes operation, the one called called g.
            '''
            if self._coefficients == 0:#FIXME: is this true?
                return self
            if self._gcd == None:
                self._gcd,self._multinv,y = \
                                 self.__egcd__(self._coefficients,self._modulo)
            self._debug_stream("gcd",self._gcd)
            self._debug_stream("x",self._multinv)
            if self._gcd != 1:
                raise ArithmeticError("The inverse of %s modulo %s "\
                                      "doens't exist!"
                                 %(self.__interpretToStr__(self._coefficients),
                                        self.__interpretToStr__(self._modulo)))
            else:
                return self._multinv#%self._modulo
        def __invert__(self):# => ~a, that means like a^-1
            res = self.__multiplicativeInverse__()
            return BinaryPolynomialModuloConstructor(res)
        #---- <<>> Shifts
        def __lshift__(self,n):# => <<
            return BinaryPolynomialModuloConstructor(self._coefficients<<n)
        def __rshift__(self,n):# => >>
            return BinaryPolynomialModuloConstructor(self._coefficients>>n)
        def __ilshift__(self,n):# => <<=
            return BinaryPolynomialModuloConstructor(self._coefficients<<n)
        def __irshift__(self,n):# => >>=
            return BinaryPolynomialModuloConstructor(self._coefficients>>n)
        def _cyclic_lshift_(self,n):
            '''
            '''
            return BinaryPolynomialModuloConstructor(self._bit_lshift_(n))
        def _bit_lshift_(self,n):
            '''Using the polynomial coefficients as a bit string, return a bit 
               string with a left side cyclic shift. It uses the modulo degree 
               to do this shift within this length.
            '''
            maxbits = self.modulodegree-1
            first = (self._coefficients << n%maxbits) & 2**maxbits-1
            second = (self._coefficients >> (maxbits-(n%maxbits))\
                                                      & 2**maxbits-1)
            return first|second
        def _cyclic_rshift_(self,n):
            '''
            '''
            return BinaryPolynomialModuloConstructor(self._bit_rshift_(n))
        def _bit_rshift_(self,n):
            '''Using the polynomial coefficients as a bit string, return a bit 
               string with a right side cyclic shift. It uses the modulo 
               degree to do this shift within this length.
            '''
            maxbits = self.modulodegree-1
            first = (self._coefficients >> n%maxbits) & 2**maxbits-1
            second = (self._coefficients << (maxbits-(n%maxbits))\
                                                      & 2**maxbits-1)
            return first|second
    return BinaryPolynomialModuloConstructor

def getBinaryPolynomialFieldModulo(wordSize):
    '''Who is chosen m(z)? [1] z^8+z^4+z^3+z+1 is the first that those the job
       (build a polynomial field), and that is the rule for the other sizes 
       under study here.
       [1] "http://crypto.stackexchange.com/questions/16017/"\
           "about-the-rijndael-aes-sbox-polynomial-subbytes"
    '''
    BinaryPolynomialFieldModulo = {
        2:0x07,#z^2+z+1
        3:0x0B,#z^3+z+1
        4:0x13,#z^4+z+1
        5:0x25,#z^5+z^2+1
        6:0x43,#z^6+z+1
        7:0x83,#z^7+z+1
        8:0x11B,#z^8+z^4+z^3+z+1 the Rijndael's original
        9:0x203,#z^9+z+1
        10:0x409,#z^10+z^3+1
        11:0x805,#z^11+z^2+1
        12:0x1009,#z^12+z^3+1
        13:0x201B,#z^13+z^4+z^3+z+1
        14:0x4021,#z^14+z^5+1
        15:0x8003,#z^15+z+1
        16:0x1002B,#z^16+z^5+z^3+z+1
    }[wordSize]
    return BinaryPolynomialFieldModulo

def getBinaryPolynomialRingModulo(wordSize):
    '''Who is chosen m'(z)? z^8+1 is the first that those the job
       (build a polynomial ring), and that is the rule for the other sizes under
       study here.
       This is quite similar to how the binary polynomial field modulo is 
       chosen.
    '''
    BinaryPolynomialRingModulo = {
        2:0x05,#z^2+1
        3:0x09,#z^3+1
        4:0x11,#z^4+1
        5:0x21,#z^5+1
        6:0x41,#z^6+1
        7:0x81,#z^7+1
        8:0x101,#z^8+1 the Rijndael's original
        9:0x201,#z^9+1
        10:0x401,#z^10+1
        11:0x801,#z^11+1
        12:0x1001,#z^12+1
        13:0x2001,#z^13+1
        14:0x4001,#z^14+1
        15:0x8001,#z^15+1
        16:0x10001,#z^16+1
    }[wordSize]
    return BinaryPolynomialRingModulo

def getMu(wordSize,official=False):
    '''Invertible element in the binary polynomial ring used in the second 
       transformation 'f' of the SBoxes.
       b(z) = mu(z) \cdot a(z) + nu(z)
       When undo the transformation:
       a(z) = mu^{-1}(z) \cdot [b(z) - nu(z)]
    '''
    if official and wordSize==8:
        return 0x1F
    Mu = {
        3:0x02,#z
        4:0x07,#z^2+z+1
        5:0x0B,#z^3+z+1
        6:0x26,#z^5+z^2+z
        7:0x26,#z^5+z^2+z
        8:0x3D,#z^5+z^4+z^3+z^2+1#0x1F,#z^4+z^3+z^2+z+1
        9:0x52,#z^6+z^4+z
        10:0x15C,#z^8+z^6+z^4+z^3+z^2
    }[wordSize]
    return Mu

def getNu(wordSize,official=False):
    '''Element of the binary polynomial ring used in the second transformation 
       'f' of the SBoxes:
       b(z) = mu(z) \cdot a(z) + nu(z)
       When undo the transformation:
       a(z) = mu^{-1}(z) \cdot [b(z) - nu(z)]
    '''
    if official and wordSize==8:
        return 0x63
    Mu = {
        3:0x02,#z
        4:0x08,#z^3
        5:0x02,#z
        6:0x25,#z^5+z^2+1
        7:0x10,#z^4
        8:0x47,#z^6+z^2+z+1#0x63,#z^6+z^5+z+1
        9:0x38,#z^5+z^4+z^3+z
        10:0x236,#z^9+z^5+z^4+z^2+z
    }[wordSize]
    return Mu


def SuperPolynomialRingModulo(modulo,variable='x',loglevel=_Logger._info):
    '''
        Polynomial ring with coefficients in  a binary polynomial field.
        TODO: more explanation.
    '''
    if type(modulo) == str and modulo.count(variable) == 0:
        raise Exception("modulo %s is not defined over %s variable"
                        %(modulo,variable))
    class SuperPolynomialRingConstructor(_Logger):
        '''
            TODO: document
        '''
        def __init__(self,value):
            _Logger.__init__(self,loglevel)
            if len(variable) != 1:
                raise NameError("The indeterminate must be "\
                                "a single character.")
            if ord('a') > variable.lower() > ord('x'):
                raise NameError("The indeterminate must be a valid "\
                                "alphabet letter.")
            self._variable = variable
            if type(value) == SuperPolynomialRingConstructor or \
               value.__class__ == SuperPolynomialRingConstructor:
                self._coefficients = value.coefficients
            elif type(value) == list:
                if len(value) == 0:
                    #TODO: build the neutral element of the first operation
                    raise NotImplementedError("Not yet available")
                firstCoefficient = value[0]
                if str(type(firstCoefficient)).\
                count('BinaryPolynomialModuloConstructor'):
                    for coefficient in value[1:]:
                        if not str(type(coefficient)).\
                        count('BinaryPolynomialModuloConstructor'):
                            raise TypeError("coefficients shall be a binary "\
                                            "polynomial field elements")
                        if firstCoefficient.modulo != coefficient.modulo:
                            raise AssertionError("All the coefficients shall "\
                                                 "be from the same field.")
            elif type(value) == str:
                self._coefficients = self.__interpretFromStr__(value)
            #TODO: are there other representations 
            #that a constructor can support?
            # - list of integers: but how to know the polynomial modulo of 
            #                     field?
            else:
                raise AssertionError("The given coefficients type '%s'"\
                                     "is not interpretable"%(type(value)))
            self._coefficients = value
            self._subfield = BinaryPolynomialModulo(\
                                self._coefficients[0].modulo,
                                self._coefficients[0].variable)
            if type(modulo) == str:
                self._modulo = self.__interpretFromStr__(modulo)
            else:
                try:#Do a last try to interpret the coefficients
                    self._modulo = int(modulo)
                except Exception,e:
                    raise AssertionError("The given modulo type '%s'"\
                                         "is not interpretable"%(type(modulo)))
            
        def __str__(self):
            '''
                Readable representation. (%s)
            '''
            return self.__interpretToStr__(self._coefficients)
        def __repr__(self):
            '''
                Unambiguous representation. (%r)
            '''
            return "%s (mod %s)"%(self.__interpretToStr__(self._coefficients),
                                  self.__interpretToStr__(self._modulo))
            
        def __hex__(self):
            '''
                String where the coefficients are compacted on an hexadecimal
                representation.
            '''
            return self.__interpretToStr__(self._coefficients,hexSubfield=True)
            
        def __interpretToStr__(self,polynomial,hexSubfield=False):
            if polynomial == 0:
                return '0'#FIXME: the neutral element of the first operation
            else:
                terms = [] #coefficients representations list
                for idx,coefficient in enumerate(polynomial):
                    exponent = len(polynomial)-idx-1
                    #FIXME: those nested 'ifs' can be simplified
                    if exponent == 0:
                        if coefficient == self._subfield(0):
                            terms.append("")
                        elif coefficient == self._subfield(1):
                            terms.append("+1")
                        else:
                            if hexSubfield:
                                terms.append("+%s"%(hex(coefficient)))
                            else:
                                terms.append("+(%s)"%(coefficient))
                    elif exponent == 1:
                        if coefficient == self._subfield(0):
                            terms.append("")
                        elif coefficient == self._subfield(1):
                            terms.append("+%s"%(self._variable))
                        else:
                            if hexSubfield:
                                terms.append("+%s%s"
                                            %(hex(coefficient),self._variable))
                            else:
                                terms.append("+(%s)%s"
                                             %(coefficient,self._variable))
                    else:
                        if coefficient == self._subfield(0):
                            terms.append("")
                        elif coefficient == self._subfield(1):
                            terms.append("+%s^%d"%(self._variable,exponent))
                        else:
                            if hexSubfield:
                                terms.append("+%s%s^%d"
                                   %(hex(coefficient),self._variable,exponent))
                            else:
                                terms.append("+(%s)%s^%d"
                                        %(coefficient,self._variable,exponent))
                collect = ''.join(["%s"%(term) for term in terms])
                if collect[0] == '+':
                    collect = collect[1:]
                return collect
        def __interpretFromStr__(self,string):
            #FIXME: simplify, that's too big for the task to do.
            terms = {}
            i = 0
            while i < len(string):
                while string[i] == ' ' or i == len(string):
                    i += 1#ignore any &nbsp;
                if string[i] == '(':
                    closer = string.find(')',i)
                    coefficient = string[i+1:closer]
                    i = closer
                elif string[i:i+2] == '0x':
                    vblePos = string.find(self._variable,i)
                    coefficient = string[i:vblePos]
                    i = vblePos
                else:
                    coefficient = self._subfield(1)
                if string[i] != self._variable:
                    i += 1
                if i == len(string):
                    terms[0] = coefficient
                    break
                if string[i] == self._variable:
                    j = i+1
                    while string[j] == ' ' or i == len(string):
                        j += 1#ignore any &nbsp;
                    if string[j] == '^':
                        closer = string.find('+',j)
                        exponent = int(string[j+1:closer])
                        i = closer
                    elif string[j] == '+':
                        exponent = 1
                        i += j+1
                elif string[i] == '+':
                    exponent = 0
                    i += 1
                else:
                    raise SyntaxError("Cannot understand %s as a polynomial "\
                                      "ring with coefficients in a binary "\
                                      "polynomial field"%(string))
                terms[exponent] = coefficient
                i += 1
            degrees = terms.keys()
            degrees.sort()
            degree = degrees[-1]
            coefficients = []
            for i in range(degree,-1,-1):
                if terms.has_key(i):
                    coefficients.append(self._subfield(terms[i]))
                else:
                    coefficients.append(self._subfield(0))
            return coefficients
        @property
        def coefficients(self):
            return self._coefficients
        @property
        def modulo(self):
            return self.__interpretToStr__(self._modulo)
        @property
        def degree(self):
            return len(self._coefficients)
        @property
        def modulodegree(self):
            return len(self._modulo)-1
        def __mul__(self,other):
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
            #TODO...
            pass
        def __imul__(self,other):# => a*=b
            bar = self * other
            return SuperPolynomialRingConstructor(bar._coefficients)
    return SuperPolynomialRingConstructor

class PolynomialRing(_Logger):
    '''This represents a polynomial over (GF(2^n))^l, with a modulo polynomial 
       composed (decomposable in roots) this becomes a algebraic ring.
       The coefficients on this polynomial ring are elements of a polynomial 
       field.
    '''
    def __init__(self,nRows,nColumns,wordSize,loglevel=_Logger._info):
        _Logger.__init__(self,loglevel)
        self.__nRows=nRows
        self.__nColumns=nColumns
        field_modulo = getBinaryPolynomialFieldModulo(wordSize)
        self._field = BinaryPolynomialModulo(field_modulo)
        
    def product(self,ax,sx):
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
        res=_deepcopy(sx)#---- FIXME: #[[0]*self.__nRows]*self.__nColumns
        for c in range(self.__nColumns):
            shifted_ax=_shift(ax,self.__nRows-1)
            for r in range(self.__nRows):
                res[r][c]=0
                for rbis in range(self.__nRows):
                    a = self._field(shifted_ax[rbis])
                    b = self._field(sx[rbis][c])
                    res[r][c]^=(a*b)._coefficients
                shifted_ax=_shift(shifted_ax,-1)
        return res

def randomBinaryPolynomial(field,degree):
    return field(randint(0,2**degree))

def randomSuperPolynomial(ring,ringDegree,field,fieldDegree):
    coefficients = []
    for i in range(ringDegree):
        coefficients.append(randomBinaryPolynomial(field,fieldDegree))
    return ring(coefficients)

if __name__ == "__main__":
    from random import randint
    #print("Use PolynomialsTest.py for testing.")
    field = BinaryPolynomialModulo('z^8+z^4+z^3+z+1',loglevel=_Logger._info)
    ring = SuperPolynomialRingModulo("x^4+1",loglevel=_Logger._debug)
    example = randomSuperPolynomial(ring,4,field,8)
    print("Random element of the polynomial ring with coefficients in a "\
          "binary polynomial field:\n\tstring:\t%s\n\trepr:\t%r\n\thex:\t%s"
          %(example,example,hex(example)))
    example._coefficients[randint(0,3)] = field(0)
    print("Eliminate one of the coefficients to test the good representation "\
          "when there is no coefficient:\n\tstring:\t%s\n\trepr:\t%r"\
          "\n\thex:\t%s"%(example,example,hex(example)))
