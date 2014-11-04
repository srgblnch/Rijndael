#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: ThirdLevel.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2014 (copyleft)
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

'''As a descendant level design, this file has the classes definitions of the 
   levels above the Rijndael operations.
'''

from Logger import Logger
from copy import deepcopy

class Word:
    def __init__(self,nRows,wordSize):
        self.__nRows=nRows
        self.__wordSize=wordSize
    def toList(self,superWord):
        '''Split an number in a set of integers with wordSize bits each
           Input: <integer> superWord
           Output: <integer array> wordsArray
           descent methods: []
           auxiliar methods: []
        '''
        wordsArray=[]
        mask=int('0b'+'1'*self.__wordSize,2)
        for i in range(self.__nRows):
            wordsArray.append((superWord>>self.__wordSize*i)&mask)
        return wordsArray
    def fromList(self,wordsArray):
        '''Concatenate a set of integers (with wordSize bits each) into one
           integer with size wordSize*len(wordList)
           Input: <integer array> wordsArray
           Output: <integer> superWord
           descent methods: []
           auxiliar methods: []
        '''
        superWord=0
        for j in range(self.__nRows):
            superWord+=wordsArray[j]<<self.__wordSize*(self.__nRows-j-1)
        return superWord

class Long:
    def __init__(self,wordSize):
        self.__wordSize=wordSize
    def toArray(self,input,length):
        '''Auxilliar method to unpack an integer to a set of smaller integers
           in an array. The size of each of the integers in the set have the
           wordSize
           Input: <integer>
           Output: <integer array>
        '''
        if input>int('0b'+('1'*length),2):
            raise Exception("(long2array)","Too big input for %d lenght"
                            %(length))
        o=[]
        #cut the input blocs of the word size
        mask=(int('0b'+('1'*self.__wordSize),2)<<(length-self.__wordSize))
        for i in range(length/self.__wordSize):
            e=(input&mask)>>(((length/self.__wordSize)-i-1)*self.__wordSize)
            o.append(int(e))
            mask>>=self.__wordSize
        return o

    def fromArray(self,input,length):
        '''Auxiliar method to pack an array of integers (with #wordSize bits)
           onto one integer.
           Input: <integer array>
           Output: <integer>
           descent methods: []
           auxiliar methods: []
        '''
        o=0
        for i in range(length/self.__wordSize):
            o|=(input[i]<<(((length/self.__wordSize)-i-1)*self.__wordSize))
        return o

class PolynomialRing:
    '''This represents a polynomial over (GF(2^n))^l, with a modulo polynomial 
       composed (decomposable in roots) this becomes a algebraic ring.
       The coefficients on this polynomial ring are elements of a polynomial field.
    '''
    def __init__(self,nRows,nColumns,wordSize):
        self.__nRows=nRows
        self.__nColumns=nColumns
        self.__polynomialsubfield=PolynomialField(wordSize)
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
                shifted_ax=shift(shifted_ax,-1)
        return res

PolynomialFieldModulo = {2:0x07,#z^2+z+1
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
                        }#[wordSize]

binlen=lambda x: len(bin(x))-2

class PolynomialField:
    '''This represents a polynomial over (GF(2^n) with a degree at most 2^{n}-1
       Because the polynomial modulo is prime (it is a root) this 
       describes an algebraic field.
    '''
    def __init__(self,degree):
        self._degree = degree
        self._modulo = PolynomialFieldModulo[degree]
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
        gcd,x,y = self._egcd(value, self._modulo)
        if gcd != 1:
            raise Exception("The inverse of %s modulo %s doens't exist!"%(value,self._modulo))
        else:
            return x%self._modulo
    def affineTransformation(self,value):
        '''Second of the transformation, called f.
        '''
        pass
    def _egcd(self,a,b):
        '''Extended Euclidean Algorithm
        '''
        x,y,u,v = 0,1,1,0
        while a != 0:
            q,r = b/a,b%a
            m,n = x-u*q,y-v*q
            b,a,x,y,u,v=a,r,u,v,m,n
        gcd = b
        return gcd,x,y

def shift(l,n):
    #---- Binary doesn't need a class
    '''cyclic rotation of the list 'l' y 'n' elements. 
       Positive n's means left, negative n's means right.
       Input:
       Output:
    '''
    return l[n:]+l[:n]

class State(Logger):
    def __init__(self,nRows,nColumns,loglevel=Logger.info):
        Logger.__init__(self,loglevel)
        self.__nRows=nRows
        self.__nColumns=nColumns
    def fromArray(self,input):
        '''Given a one dimensional array, convert it to a r*c array following:
           s[r,c] = in[r+rc] for 0<=r<nRows and 0<=c<nColumns
           Input: <integer array> 1d
           Output: <integer arrays> 2d
        '''
        #---- FIXME: what happens if the size of input is not r*c?
        #       if exceeds, the rest are ignored;
        #       if not enough, empty cells
        state=[None]*self.__nRows
        for i in range(len(input)):
            row=i%self.__nRows
            if row==i:
                state[row]=[input[i]]
            else:
                state[row].append(input[i])
        for i in range(self.__nRows):
            self.debug_stream("state[%d]"%i,state[i])
        self.debug_stream("makeArray",state)
        return state

    def toArray(self,state):
        '''From a r*c array, returns a one dimensional array following:
           out[r+rc] = s[r,c]  for 0<=r<nRows and 0<=c<nColumns
           Input: <integer arrays> 2d
           Output: <integer array> 1d
        '''
        output=[]
        for j in range(self.__nColumns):
            for i in range(self.__nRows):
                output.append(state[i][j])
        self.debug_stream("unmakeArray",output)
        return output
