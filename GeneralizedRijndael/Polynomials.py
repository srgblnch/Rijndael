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

from Logger import Logger
from ThirdLevel import shift,binlen
from copy import copy,deepcopy

def BinaryPolynomialModulo(modulo,variable='x',loglevel=Logger.info):
    '''BinaryPolynomialModulo is a builder for the given modulo. The returning
       object can generate elements in this field or ring (depending on the 
       reducibility of the modulo polynomial).
       
       The integer representation will use binary representation to assign the 
       MSB to highest degree and the LSB to the 0 degree. For the string 
       representation the sage notation has been take as inspiration.
       
       Arguments:
       - modulo: (mandatory) an integer or an string representation of a 
         polynomial (like 'x^8+x^4+x^3+x+1' that's equivalent to 0x11B).
       - variable: by default is 'x' and it is only used for the output strings
         representing the polynomials.
       - loglevel: by default info, based on the superclass Logger enumeration.
       
       Example:
       >>> import Polynomials
       >>> field = Polynomials.BinaryPolynomialModulo('x^8+x^4+x^3+x+1')
    '''
    #This help is shown when
    #>>> Polynomials.BinaryPolynomialModulo?
    class BinaryPolynomialModuloConstructor(Logger):
        def __init__(self,value):
            '''Polynomial defined by an integer or an string representation 
               of an element of the field or ring defined when made the builder
               object.
               
               Argument:
               - value: (mandatory) the value to be interpreted as a binary 
                 polynomial finite field or ring.
                 
               Example:
               >>> from Polynomials import BinaryPolynomialModulo
               >>> field = BinaryPolynomialModulo('x^8+x^4+x^3+x+1')
               >>> a = field(73); a
               x^6+x^3+1 (mod x^8+x^4+x^3+x+1)
            '''
            #This help is shown when, from the last one
            #>>> field?
            #FIXME: improve the logging on this class
            Logger.__init__(self,loglevel)
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
            self.debug_stream("coefficients", self._coefficients)
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
            self.debug_stream("modulo", self._modulo)
            #if the degree of coefficients > degree of modulo, do the reduction
            if self.degree >= len("{0:b}".format(self._modulo)):
                q,r = self.__division__(self._coefficients,self._modulo)
                self._coefficients = r
                self.debug_stream("reduced coefficients", self._coefficients)
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
        def isZero(self):
            '''Neutral element of the first operation, addition.'''
            return self._coefficients == 0
        @property
        def isOne(self):
            '''Neutral element of the second operation, product.'''
            return self._coefficients == 1
        def __iter__(self):
            return iter("{0:b}".format(self._coefficients))
        def iter(self):
            return self.__iter__()
        def __type__(self):
            return self.__class__
        def checkTypes(function):
            '''Decorator to precheck the input parameters on some of the 
               operations.
            '''
            def comparator(self,other):
                if other.__class__ != BinaryPolynomialModuloConstructor:
                    raise EnvironmentError("Cannot compare with non "\
                                           "polynomials (%s)"%(type(other)))
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
        def __hex__(self):
            '''
            '''
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
                        #equiv to x^1 but short
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
                    value |= 1<<1#x^1
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
            if self._coefficients == other._coefficients:
                return True
            return False
        @checkTypes
        def __ne__(self,other):# => a!=b
            if self.__eq__(other):
                return False
            return True
        #Meaningless operators in polynomials:
        # operator.__lt__(a,b) => a<b
        # operator.__le__(a,b) => a<=b
        # operator.__gt__(a,b) => a>b
        # operator.__ge__(a,b) => a>=b
        #---- #Operations
        #---- Addition
        @checkTypes
        def __add__(self,other):# => a+b
            a = copy(self.coefficients)
            b = copy(other.coefficients)
            return BinaryPolynomialModuloConstructor(a^b)
        def __iadd__(self,other):# => a+=b
            bar = self + other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        #---- Substraction
        def __neg__(self):# => -a
            return self
        def __sub__(self, other):# => a-b
            bar = -other
            a = copy(self.coefficients)
            b = copy(other.coefficients)
            return BinaryPolynomialModuloConstructor(a^b)
        def __isub__(self,other):# => a-=b
            bar = self - other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        #---- Product
        @checkTypes
        def __mul__(self,other):# => a*b
            '''
            '''
            a = copy(self._coefficients)
            b = copy(other._coefficients)
            res = self.__multiply__(a,b)
            self.debug_stream("c = a * b = %s * %s = %s"
                              %(self.__interpretToStr__(a),
                                self.__interpretToStr__(b),
                                self.__interpretToStr__(res)))
            return BinaryPolynomialModuloConstructor(res)
        def __imul__(self,other):# => a*=b
            bar = self * other
            return BinaryPolynomialModuloConstructor(bar._coefficients)
        def xtimes(self):
            return BinaryPolynomialModuloConstructor(self._coefficients << 1)
        def __multiply__(self,a,b):
            '''
            '''
#            aOnes = "{0:b}".format(a).count('1')
#            bOnes = "{0:b}".format(b).count('1')
#            self.info_stream("a has %d ones and b has %d ones"%(aOnes,bOnes))
#            if aOnes < bOnes:
#                # a <-> b
#                a,b = b,a
#                self.info_stream("a and b swapped to have on b the minimum"\
#                                 "number of 1s.")
            self.debug_stream("a %s"%self.__interpretToStr__(a))
            self.debug_stream("b %s"%self.__interpretToStr__(b))
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
            #j = 0
            #aShifted = a
            #while j < i:#aShifted = a << i modulo m
            #    aShifted <<= 1
            #    if aShifted > self._modulo:
            #        aShifted ^= self._modulo
            #    j += 1
            newerAccum = accum ^ aShifted
            if bit:
                self.debug_stream("aShifted: %s"%
                                 self.__interpretToStr__(aShifted))
                return newerAccum
            else:
                return accum
        #---- Division
        def __division__(self,a,b):
            '''
            '''
            #FIXME: check division by 0 => ZeroDivisionError
            self.debug_stream("\n<division>")
            gr_a = len("{0:b}".format(a))-1
            gr_b = len("{0:b}".format(b))-1
            q = 0
            r = a
            self.debug_stream("a",a)
            self.debug_stream("b",b)
            self.debug_stream("q",q)
            self.debug_stream("r",r)
            shift = gr_a-gr_b
            while len("{0:b}".format(r))>=len("{0:b}".format(b)) and \
                  shift >= 0:
                #FIXME: this means deg(r) >= deg(b), but it's horrible
                gr_r = len("{0:b}".format(r))-1
                if shift > 0:
                    temp = int("{0:b}".format(r)[0:-shift],2)<<shift
                else:
                    temp = r
                self.debug_stream("temp",temp)
                subs = b << shift
                self.debug_stream("subs",subs)
                if len("{0:b}".format(temp)) == len("{0:b}".format(subs)):
                    bar = temp ^ subs
                    self.debug_stream("temp ^subs",bar)
                    if shift > 0:
                        mask = int('1'*shift,2)
                        q = q | 1<<(shift)
                        r = bar | (a & mask)
                    else:
                        q |= 1
                        r = bar
                self.debug_stream("q",q)
                self.debug_stream("r",r)
                gr_a -= 1
                shift = gr_a-gr_b
            self.debug_stream("<\\division>\n")
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
        #---- TODO: Multiplicative inverse 
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
            self.debug_stream("u",u)
            self.debug_stream("v",v)
            g1,g2,h1,h2 = 1,0,0,1
            self.debug_stream("g1",g1)
            self.debug_stream("g2",g2)
            self.debug_stream("h1",h1)
            self.debug_stream("h2",h2)
            while u != 0:
                j = len("{0:b}".format(u))-len("{0:b}".format(v))
                if j < 0:
                    self.debug_stream("%d < 0"%j)
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
                self.debug_stream("\tu",u)
                self.debug_stream("\tg1",g1)
                self.debug_stream("\th1",h1)
            d,g,h = v,g2,h2
            self.debug_stream("d",d)
            self.debug_stream("g",g)
            self.debug_stream("h",h)
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
            gcd,x,y = self.__egcd__(self._coefficients,self._modulo)
            self.debug_stream("gcd",gcd)
            self.debug_stream("x",x)
            self.debug_stream("y",y)
            if gcd != 1:
                raise ArithmeticError("The inverse of %s modulo %s "\
                                      "doens't exist!"
                                 %(self.__interpretToStr__(self._coefficients),
                                        self.__interpretToStr__(self._modulo)))
            else:
                return x#%self._modulo
        def __invert__(self):# => ~a, that means like a^-1
            res = self.__multiplicativeInverse__()
            return BinaryPolynomialModuloConstructor(res)
        #---- Shifts
    #    #TODO: shift operations (
    #    #      - operator.__lshift__ => <<
    #    #      - operator.__rshift__ => >>
    #    #      - operator.__ilshift__ => <<=
    #    #      - operator.__irshift__ => >>=
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
#
class BinaryPolynomialField(Logger):
    '''This represents a polynomial over (GF(2^n) with a degree at most 2^{n}-1
       Because the polynomial modulo is prime (it is a root) this 
       describes an algebraic field.
       This is used for the multiplicative inverse of the SBoxes and from the 
       Polynomial Ring with coefficients in a polynomial field (MixColumns).
    '''
    def __init__(self,degree,loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        self._degree = degree
        self._modulo = getBinaryPolynomialFieldModulo(degree)

    def product(self,a,b):
        '''multiplication of two polynomials reduced modulo m(z).
           Input: <integer> a,b (polynomial bit representations)
                  <integer> m (modulo polynomial)
           Output: <integer> r = a*b (mod m)
        '''
        b_=b
        xor=[]
        a_i=[a]
        for i in range(binlen(b)):
            if b_&1:
                xor.append(a_i[len(a_i)-1])
            b_>>=1
            a_i.append(self.xtime(a_i[len(a_i)-1]))
        r=0
        for x in xor:
            r^=x
        return r

    def xtime(self,a):
        '''polynomial product by x reduced modulo m.
           Input: <integer> a (polynomial bit representation)
                  <integer> m (modulo polynomial)
           Output: <integer> a*x (mod m)
        '''
        a<<=1
        if a&(1<<binlen(self._modulo)-1): a^=self._modulo
        return a

    def multiplicativeInverse(self,value):
        '''Multiplicative inverse based on ...
           Input: <integer> a (polynomial bit representation)
                  <integer> m (modulo polynomial)
           Output: <integer> a^-1: a*a^-1 = 1 (mod m)
           This it the first of the two transformations for the SBoxes in the 
           subBytes operation, the one called called g.
        '''
        if value == 0:#FIXME: is this true?
            return value
        gcd,x,y = self._egcd(value, self._modulo)
        if gcd != 1:
            raise Exception("The inverse of %s modulo %s doens't exist!"
                            %(value,self._modulo))
        else:
            return x#%self._modulo

    def _egcd(self,a,b):
        '''Extended Euclidean gcd (Greatest Common Divisor) Algorithm
           Input: <integer> a (polynomial bit representation)
                  <integer> b (polynomial bit representation)
           Output: <integer> gcd
                   <integer> x (polynomial bit representation)
                   <integer> y (polynomial bit representation)
        '''
        x,y,u,v = 0,1,1,0
        while a != 0:
            q,r = b/a,b%a
            m,n = x-u*q,y-v*q
            b,a,x,y,u,v=a,r,u,v,m,n
        gcd = b
        return gcd,x,y
        

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

def getMu(wordSize):
    '''Invertible element in the binary polynomial ring used in the second 
       transformation 'f' of the SBoxes.
       b(z) = mu(z) \cdot a(z) + nu(z)
    '''
    Mu = {
        8:0xF1,#z^7+z^6+z^5+z^4+1
    }[wordSize]
    return Mu

def getNu(wordSize):
    '''Invertible element in the binary polynomial ring used in the second 
       transformation 'f' of the SBoxes.
       b(z) = mu(z) \cdot a(z) + nu(z)
    '''
    Mu = {
        8:0xC4,#z^7+z^6+z^2
        #8:0x63,#Z^6+z^5+z+1
    }[wordSize]
    return Mu

#class BinaryPolynomialRing(Logger):
#    '''This represents a binary polynomial non-prime modulo to compute the 
#       affine transformation needed for the Sboxes.
#    '''
#    def __init__(self,modulo,loglevel=Logger.info):
#        Logger.__init__(self,loglevel)
#        self._modulo = modulo
#        self._degree = len(bin(degree)-2)
#    
#    def affineTransformation(self,value):
#        '''Second of the transformation, called f.
#           Input: <integer> a (polynomial bit representation)
#           Output: <integer> b (polynomial bit representation)
#           b(z) = u(z) \cdot a(z) + v(z)
#        '''
#        pass
#        #TODO: this is returning None by now

class PolynomialRing:
    '''This represents a polynomial over (GF(2^n))^l, with a modulo polynomial 
       composed (decomposable in roots) this becomes a algebraic ring.
       The coefficients on this polynomial ring are elements of a polynomial 
       field.
    '''
    def __init__(self,nRows,nColumns,wordSize):
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__polynomialsubfield=BinaryPolynomialField(wordSize)
        #self._field_modulo = BinaryPolynomialModulo(\
        #                             getBinaryPolynomialFieldModulo(wordSize))
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
        res=deepcopy(sx)#---- FIXME: #[[0]*self.__nRows]*self.__nColumns
        for c in range(self.__nColumns):
            shifted_ax=shift(ax,self.__nRows-1)
            for r in range(self.__nRows):
                res[r][c]=0
                for rbis in range(self.__nRows):
                    res[r][c]^=self.__polynomialsubfield.\
                                          product(shifted_ax[rbis],sx[rbis][c])
#                    a = self._field_modulo(shifted_ax[rbis])
#                    b = self._field_modulo(sx[rbis][c])
#                    res[r][c]^=(a*b)._coefficients
                shifted_ax=shift(shifted_ax,-1)
        return res

def printAsPolynomial(value,vble='z'):
    if value == 0:
        return '0'
    else:
        cR = [] #coefficients representations list
        degree = len(bin(value))-2
        #print("\t\t%s"%(bin(value)))
        for idx,bit in enumerate(bin(value)[2:]):
            exp = degree-idx-1
            #print("\t\t(%s,%s)"%(exp,bit))
            if bit == '0':
                pass
            elif bit == '1':
                if exp > 1:
                    cR.append("%s^%d"%(vble,exp))
                elif exp == 1:
                    cR.append("%s"%(vble))
                elif exp == 0:
                    cR.append("1")
                else:
                    cR.append("?")#This should never happen
            else:
                cR.append("?")#This should never happen
        joining = ''
        for e in cR:
            if len(joining) == 0:
                joining = "%s"%(e)
            else:
                joining = ''.join("%s+%s"%(joining,e))
        #print("\t\tpolynomial %s"%(joining))
        return joining

from optparse import OptionParser
from random import randint

def testBinaryPolynomial(value,degree,field=True):
    level=Logger.info#debug
    if field:
        getModulo = getBinaryPolynomialFieldModulo
    else:
        getModulo = getBinaryPolynomialRingModulo
    modulo = BinaryPolynomialModulo(getModulo(degree),
                                    loglevel=level)
    sample = modulo(value)
    zero = modulo(0)
    print("\nTesting: %s = %s (%s) as polynomial %r"
          %(value,hex(value),bin(value),sample))
    product = sample*sample
    print("\t(%27s)^2 =\t(%27s) = %s = %s "%(sample,product,
                                             bin(product._coefficients),
                                             hex(product._coefficients)))
    i = 3
    while product != sample:#i <= degree*52:
        product = sample*product
        print("\t(%27s)^%d =\t(%27s) = %s = %s "%(sample,i,product,
                                                  bin(product._coefficients),
                                                  hex(product._coefficients)))
        if i == 2**degree:
            print("\tat %d break!"%(i))
            break
        if product == zero:
            print("\tat %d it decays to zero!"%(i))
            break
        i += 1
    print("\n")
    i = 1
    product = sample
    xtime = sample + modulo(1)
    while (i <= 1 and i > 2**degree) or xtime != sample:#i <= degree*10:
        xtime = product.xtimes()
        print("\t%2d xtime(%27s) =\t(%27s) = %s = %s "%(i,product,xtime,
                                                      bin(xtime._coefficients),
                                                     hex(xtime._coefficients)))
        product = xtime
        if i == 2**degree:
            print("\tat %d break!"%(i))
            break
        if product == zero:
            print("\tat %d it decays to zero!"%(i))
            break
        i += 1
    print("\n")
    try:
        inverse = ~sample
        print("\t(%27s)^-1 =\t(%27s) = %s = %s "%(sample,inverse,
                                                  bin(inverse._coefficients),
                                                  hex(inverse._coefficients)))
        resample = ~inverse
        print("\t(%27s)^-1 =\t(%27s) = %s = %s "%(inverse,resample,
                                                  bin(resample._coefficients),
                                                  hex(resample._coefficients)))
    except Exception,e:
        print(e)
    print("\n")

def getBinaryPolinomialFieldInverse(value):
    '''From the table C.5 of the 'Design of Rijndael' book. 
       For testing purposes.
    '''
    table_C5 = [
# 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
[0x00,0x01,0x8D,0xF6,0xCB,0x52,0x7B,0xD1,0xE8,0x4F,0x29,0xC0,0xB0,0xE1,0xE5,0xC7],#0x0
[0x74,0xB4,0xAA,0x4B,0x99,0x2B,0x60,0x5F,0x58,0x3F,0xFD,0xCC,0xFF,0x40,0xEE,0xB2],#0x1
[0x3A,0x6E,0x5A,0xF1,0x55,0x4D,0xA8,0xC9,0xC1,0x0A,0x98,0x15,0x30,0x44,0xA2,0xC2],#0x2
[0x2C,0x45,0x92,0x6C,0xF3,0x39,0x66,0x42,0xF2,0x35,0x20,0x6F,0x77,0xBB,0x59,0x19],#0x3
[0x1D,0xFE,0x37,0x67,0x2D,0x31,0xF5,0x69,0xA7,0x64,0xAB,0x13,0x54,0x25,0xE9,0x09],#0x4
[0xED,0x5C,0x05,0xCA,0x4C,0x24,0x87,0xBF,0x18,0x3E,0x22,0xF0,0x51,0xEC,0x61,0x17],#0x5
[0x16,0x5E,0xAF,0xD3,0x49,0xA6,0x36,0x43,0xF4,0x47,0x91,0xDF,0x33,0x93,0x21,0x3B],#0x6
[0x79,0xB7,0x97,0x85,0x10,0xB5,0xBA,0x3C,0xB6,0x70,0xD0,0x06,0xA1,0xFA,0x81,0x82],#0x7
[0x83,0x7E,0x7F,0x80,0x96,0x73,0xBE,0x56,0x9B,0x9E,0x95,0xD9,0xF7,0x02,0xB9,0xA4],#0x8
[0xDE,0x6A,0x32,0x6D,0xD8,0x8A,0x84,0x72,0x2A,0x14,0x9F,0x88,0xF9,0xDC,0x89,0x9A],#0x9
[0xFB,0x7C,0x2E,0xC3,0x8F,0xB8,0x65,0x48,0x26,0xC8,0x12,0x4A,0xCE,0xE7,0xD2,0x62],#0xA
[0x0C,0xE0,0x1F,0xEF,0x11,0x75,0x78,0x71,0xA5,0x8E,0x76,0x3D,0xBD,0xBC,0x86,0x57],#0xB
[0x0B,0x28,0x2F,0xA3,0xDA,0xD4,0xE4,0x0F,0xA9,0x27,0x53,0x04,0x1B,0xFC,0xAC,0xE6],#0xC
[0x7A,0x07,0xAE,0x63,0xC5,0xDB,0xE2,0xEA,0x94,0x8B,0xC4,0xD5,0x9D,0xF8,0x90,0x6B],#0xD
[0xB1,0x0D,0xD6,0xEB,0xC6,0x0E,0xCF,0xAD,0x08,0x4E,0xD7,0xE3,0x5D,0x50,0x1E,0xB3],#0xE
[0x5B,0x23,0x38,0x34,0x68,0x46,0x03,0x8C,0xDD,0x9C,0x7D,0xA0,0xCD,0x1A,0x41,0x1C],#0xF
]
    c = value&0x0f
    r = (value&0xf0)>>4
    #print("%s => (%s,%s)"%(hex(value),hex(r),hex(c)))
    return table_C5[r][c]

def testTableC5():
    degree = 8
    field = BinaryPolynomialModulo(getBinaryPolynomialFieldModulo(degree))
    ok,failed = 0,0
    for i in range(256):
        p = field(i)
        calc = ~p
        table = getBinaryPolinomialFieldInverse(i)
        if calc._coefficients != table:
            print("Alert for %4s (%27s):\ttable say %4s (%27s) and "\
                  "calculation %5s (%27r)"
                  %(hex(i),printAsPolynomial(i),
                    hex(table),printAsPolynomial(table),
                    hex(calc),calc))
            failed+=1
            pass
        else:
            
            if p.isZero or p * calc == field(1):
                ok+=1
            else:
                print("Alert %s * %s != %r"%(p,calc,field(1)))
    return (ok,failed)
    #return "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")

def testPolynomialInverse(degree):
    field = BinaryPolynomialModulo(getBinaryPolynomialFieldModulo(degree))
    ok,failed = 0,0
    for i in range(2**degree):
        p = field(i)
        calc = ~p
        if p.isZero or p * calc == field(1):
            ok += 1
        else:
            print("Alert %s * %s != %r"%(p,calc,field(1)))
    return (ok,failed)
    #return "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")

def getRijndaelsAffineMapping(value,inverse=False):
    '''From the table C.3 and its invers C.4 of the 'Design of Rijndael' book.
       For testing purposes.
    '''
    table_C3 = [
# 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
[0x63,0x7C,0x5D,0x42,0x1F,0x00,0x21,0x3E,0x9B,0x84,0xA5,0xBA,0xE7,0xF8,0xD9,0xC6],#0x0
[0x92,0x8D,0xAC,0xB3,0xEE,0xF1,0xD0,0xCF,0x6A,0x75,0x54,0x4B,0x16,0x09,0x28,0x37],#0x1
[0x80,0x9F,0xBE,0xA1,0xFC,0xE3,0xC2,0xDD,0x78,0x67,0x46,0x59,0x04,0x1B,0x3A,0x25],#0x2
[0x71,0x6E,0x4F,0x50,0x0D,0x12,0x33,0x2C,0x89,0x96,0xB7,0xA8,0xF5,0xEA,0xCB,0xD4],#0x3
[0xA4,0xBB,0x9A,0x85,0xD8,0xC7,0xE6,0xF9,0x5C,0x43,0x62,0x7D,0x20,0x3F,0x1E,0x01],#0x4
[0x55,0x4A,0x6B,0x74,0x29,0x36,0x17,0x08,0xAD,0xB2,0x93,0x8C,0xD1,0xCE,0xEF,0xF0],#0x5
[0x47,0x58,0x79,0x66,0x3B,0x24,0x05,0x1A,0xBF,0xA0,0x81,0x9E,0xC3,0xDC,0xFD,0xE2],#0x6
[0xB6,0xA9,0x88,0x97,0xCA,0xD5,0xF4,0xEB,0x4E,0x51,0x70,0x6F,0x32,0x2D,0x0C,0x13],#0x7
[0xEC,0xF3,0xD2,0xCD,0x90,0x8F,0xAE,0xB1,0x14,0x0B,0x2A,0x35,0x68,0x77,0x56,0x49],#0x8
[0x1D,0x02,0x23,0x3C,0x61,0x7E,0x5F,0x40,0xE5,0xFA,0xDB,0xC4,0X99,0x86,0xA7,0xB8],#0x9
[0x0F,0x10,0x31,0x2E,0x73,0x6C,0x4D,0x52,0xF7,0xE8,0xC9,0xD6,0x8B,0x94,0xB5,0xAA],#0xA
[0xFE,0xE1,0xC0,0xDF,0x82,0x9D,0xBC,0xA3,0x06,0x19,0x38,0x27,0x7A,0x65,0x44,0x5B],#0xB
[0x2B,0x34,0x15,0x0A,0x57,0x48,0x69,0x76,0xD3,0xCC,0xED,0xF2,0xAF,0xB0,0x91,0x8E],#0xC
[0xDA,0xC5,0xE4,0xFB,0xA6,0xB9,0x98,0x87,0x22,0x3D,0x1C,0x03,0x5E,0x41,0x60,0x7F],#0xD
[0xC8,0xD7,0xF6,0xE9,0xB4,0xAB,0x8A,0x95,0x30,0x2F,0x0E,0x11,0x4C,0x53,0x72,0x6D],#0xE
[0X39,0x26,0x07,0x18,0x45,0x5A,0x7B,0x64,0xC1,0xDE,0xFF,0xE0,0xBD,0xA2,0x83,0x9C],#0xF
]
    table_C4 = [
# 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF
[0x05,0x4F,0x91,0xDB,0x2C,0x66,0xB8,0xF2,0x57,0x1D,0xC3,0x89,0x7E,0x34,0xEA,0xA0],#0x0
[0xA1,0xEB,0x35,0x7F,0x88,0xC2,0x1C,0x56,0xF3,0xB9,0x67,0x2D,0xDA,0x90,0x4E,0x04],#0x1
[0x4C,0x06,0xD8,0x92,0x65,0x2F,0xF1,0xBB,0x1E,0x54,0x8A,0xC0,0x37,0x7D,0xA3,0xE9],#0x2
[0xE8,0xA2,0x7C,0x36,0xC1,0x8B,0x55,0x1F,0xBA,0xF0,0x2E,0x64,0x93,0xD9,0x07,0x4D],#0x3
[0x97,0xDD,0x03,0x49,0xBE,0xF4,0x2A,0x60,0xC5,0x8F,0x51,0x1B,0xEC,0xA6,0x78,0x32],#0x4
[0x33,0x79,0xA7,0xED,0x1A,0x50,0x8E,0xC4,0x61,0x2B,0xF5,0xBF,0x48,0x02,0xDC,0x96],#0x5
[0xDE,0x94,0x4A,0x00,0xF7,0xBD,0x63,0x29,0x8C,0xC6,0x18,0x52,0xA5,0xEF,0x31,0x7B],#0x6
[0x7A,0x30,0xEE,0xA4,0x53,0x19,0xC7,0x8D,0x28,0x62,0xBC,0xF6,0x01,0x4B,0x95,0xDF],#0x7
[0x20,0x6A,0xB4,0xFE,0x09,0x43,0x9D,0xD7,0x72,0x38,0xE6,0xAC,0x5B,0x11,0xCF,0x85],#0x8
[0x84,0xCE,0x10,0x5A,0xAD,0xE7,0x39,0x73,0xD6,0x9C,0x42,0x08,0xFF,0xB5,0x6B,0x21],#0x9
[0x69,0x23,0xFD,0xB7,0x40,0x0A,0xD4,0x9E,0x3B,0x71,0xAF,0xE5,0x12,0x58,0x86,0xCC],#0xA
[0xCD,0x87,0x59,0x13,0xE4,0xAE,0x70,0x3A,0x9F,0xD5,0x0B,0x41,0xB6,0xFC,0x22,0x68],#0xB
[0xB2,0xF8,0x26,0x6C,0x9B,0xD1,0x0F,0x45,0xE0,0xAA,0x74,0x3E,0xC9,0x83,0x5D,0x17],#0xC
[0x16,0x5C,0x82,0xC8,0x3F,0x75,0xAB,0xE1,0x44,0x0E,0xD0,0x9A,0x6D,0x27,0xF9,0xB3],#0xD
[0xFB,0xB1,0x6F,0x25,0xD2,0x98,0x46,0x0C,0xA9,0xE3,0x3D,0x77,0x80,0xCA,0x14,0x5E],#0xE
[0x5F,0x15,0xCB,0x81,0x76,0x3C,0xE2,0xA8,0x0D,0x47,0x99,0xD3,0x24,0x6E,0xB0,0xFA],#0xF
]
    c = value&0x0f
    r = (value&0xf0)>>4
    #print("%s => (%s,%s)"%(hex(value),hex(r),hex(c)))
    if inverse:
        table = table_C4
    else:
        table = table_C3
    return table[r][c]

def testTablesC3and4():
    ok,failed = 0,0
    for a in range(256):
        b = getRijndaelsAffineMapping(a)
        c = getRijndaelsAffineMapping(b,inverse=True)
        if a != c:
            print("Alert for %4s (%27s):\n"\
                  "\ttable C3 say                %4s (%27s) and\n"\
                  "\tinverting with table C4 say %4s (%27s)"
                  %(hex(a),printAsPolynomial(a),
                    hex(b),printAsPolynomial(b),
                    hex(c),printAsPolynomial(c)))
            failed+=1
        else:
            ok+=1
    #TODO: test that C3 transformation corresponds with the affine mapping
    #      and the C4 transformation with the inversion of the affine mapping
    return (ok,failed)
    #return "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")

def testAffineMapping(degree=8):
    if degree == 8:
        ok,failed = testTablesC3and4()
        msg = "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")
        print("Check with the Rijndael's table c3 and c4: %s\n"%(msg))
        if failed != 0:
            return
    ring = BinaryPolynomialModulo(getBinaryPolynomialRingModulo(degree),
                                  variable='z')
    mu = ring(getMu(degree))
    inv_mu = ~mu
    nu = ring(getNu(degree))
    inv_nu = ~nu
    ok,failed = 0,0
    for i in range(256):
        a = ring(i)
        b = (mu * a) + nu
        if degree == 8:
            b_ = getRijndaelsAffineMapping(a._coefficients)
        c = (inv_mu * b) + inv_nu
        if degree == 8:
            c_ = getRijndaelsAffineMapping(b._coefficients,inverse=True)
        if a != c:
            if degree == 8 and b._coefficients != b_:
                about_b = "table c3 say %s = %s"%(b_,printAsPolynomial(b_))
            else:
                about_b = ""
            if degree == 8 and c._coefficients != c_:
                about_c = "table c4 say %s = %s"%(c_,printAsPolynomial(c_))
            else:
                about_c = ""
            print("Alert for a = %s =\t  %r:\n"\
                  "\tb = (mu*a)+nu =\t  %27s = %s\t(%s)\n"\
                  "\tc = (~mu*b)+~nu = %27s = %s\t(%s)"
                  %(a._coefficients,a,b,b._coefficients,about_b,
                    c,c._coefficients,about_c))
            failed+=1
        else:
            ok+=1
    print("\nFor degree %d, the affine transfomation has been "\
          "b(z) = %s * a(z) + %s. (mu=%s,nu=%s)\n"\
          "And the inverse operation                       "\
          "a(z) = %s * b(z)+ %s. (~mu=%s,~nu=%s)\n"
          %(degree,mu,nu,hex(mu._coefficients),hex(nu._coefficients),
            inv_mu,inv_nu,hex(inv_mu._coefficients),hex(inv_nu._coefficients)))
    return (ok,failed)
    #return "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")


def main():
    '''Test the correct functionality of the Polynomial Field and Ring classes.
    '''
    parser = OptionParser()
    parser.add_option('',"--binary-polynomial-field",type="int",
                     help="Numerical representation of the polynomial to test")
    parser.add_option('',"--binary-polynomial-ring",type="int",
                     help="Numerical representation of the polynomial to test")
    parser.add_option('',"--table-c5",action="store_true",
                      help="Test the table C5 from the 'Design of "\
                           "Rijndael' book ")
    parser.add_option('',"--test-field",type='int',
                      help="Test all the elements in a field if their product"\
                      "with the inverse returns the neutral element z^0")
    parser.add_option('',"--test-all-fields",action="store_true",
                      help="Loops over all available fields doing "\
                      "--test-field on it.")
#    parser.add_option('',"--test-c3-c4",action="store_true",
#                      help="Test the tables C3 and C4 from the 'Design of "\
#                           "Rijndael' book ")
    parser.add_option('',"--test-affine-mapping",action="store_true",
                      help="Test the finite binary polynomial ring")
    (options, args) = parser.parse_args()
    degree=8
    #print("options: %s"%(options))

    #This test the multiplicative inverse, 
    #the first part of the two SBox transformations
    if options.binary_polynomial_field:
        testBinaryPolynomial(options.binary_polynomial_field,degree)
    if options.binary_polynomial_ring:
        testBinaryPolynomial(options.binary_polynomial_ring,degree,field=False)
    elif options.table_c5:
        ok,failed = testTableC5()
        msg = "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")
        print("Check with the Rijndael's table c5: %s\n"%(msg))
    elif options.test_all_fields:
        import time
        for i in range(16,1,-1):
            start_t = time.time()
            res = testPolynomialInverse(i)
            end_t = time.time()
            print("For F_{2^%d}, test elements:\t%s\t(%gseconds)"
                  %(i,res,end_t-start_t))
        print("\n")
    elif options.test_field:
        ok,failed = testPolynomialInverse(options.test_field)
        msg = "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")
        print("For F_{2^%d}, test elements: %s\n"
              %(options.test_field,msg))
#    elif options.test_c3_c4:
#        ok,failed = testTablesC3and4()
#        msg = "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")
#        print("Check with the Rijndael's table c3 and c4: %s\n"
#              %(msg))
    elif options.test_affine_mapping:
        ok,failed = testAffineMapping()
        msg = "%d ok %s"%(ok,"but failed %s"%(failed) if failed >0 else "")
        print("Check the binary polynomial ring: %s"%(msg))
    else:
        #TODO: loop with a bigger sample set.
#        values = range(6)
#        for i in range(3):
#            values.append(randint(1,2**degree))
#        values.sort()
#        for value in values:
#            testBinaryPolynomial(value,degree)
        pass
    #TODO: test the affine transformation,
    #the second part of the two SBox transformations
    #...
    
    #TODO: test the polynomial ring 
    #with coefficients elements as polynomial field
    

if __name__ == "__main__":
    main()
