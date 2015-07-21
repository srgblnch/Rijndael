##############################################################################
##
## file: polynomials.py
##
## developers history & copyleft: Sergi Blanch-Torn\'e
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

from copy import copy

class Polynomial:
    def __init__(self,value,variable='x'):
        '''Polynomial defined by coefficients in a field or a ring.
           The coefficients are described in a list where the first is biggest.
           Example: polynomials.Polynomial([1,0,2,3],variable='z')
           means: z^3 + 2z^1 + 3
        '''
        #TODO: it must allow to define a polynomial over more than the integers
        #      that is, for example, a finite field or ring, then the
        #      comparisons with 1 or 0, must change to request that field who 
        #      is its identity elements in the additive operation and which one
        #      in the multiplicative operation.
        self._variable = variable
        if type(value) == Polynomial:
            self._coefficients = value.coefficients
        elif type(value) == list:
            if (value.count(0) == len(value)):
                self._coefficients = []
            elif len(value)>0:
                self._coefficients = value
                #remove null elements on the left side coefficients
                while self._coefficients[0] == 0:
                    self._coefficients.pop(0)
                #check all remaining elements have same integer type
                for i in range(len(self._coefficients)):
                    if type(self._coefficients[0]) != type(self._coefficients[i]):
                        raise ValueError("All the polynomial coefficients must "\
                                         "be the same type")
        else:
            self._coefficients = []
    @property
    def coefficients(self):
        return self._coefficients
    @property
    def degree(self):
        return len(self._coefficients)-1
    @property
    def variable(self):
        return self._variable
    def isZero(self):
        return not bool(len(self._coefficients))
    #TODO: another isFunc with the neutral element of the second operation
    def checkTypes(function):
        '''Decorator to precheck the input parameters on some of the operations
        '''
        def comparator(self,other):
            if not self.variable == other.variable:
                raise EnvironmentError("Uncompatible polynomials")
            #TODO: check if their coefficients have the same type
            return function(self,other)
        return comparator
    def __repr__(self):
        if self.isZero():
            return '0'#FIXME: the neutral element of the first operation
        else:
            cR = [] #coefficients representations list
            #FIXME: review this naming
            for exponent,coefficient in enumerate(self._coefficients):
                if not coefficient == 0:
                    #FIXME: Improve this dirted casuistry...
                    if self.degree-exponent > 0:
                        cR.append("%s%s%s"
                           %('' if coefficient == 0 else \
                             '+' if coefficient == 1 else \
                             '+%s*'%(coefficient) if coefficient > 1 else \
                             '%s*'%(coefficient),
                             self._variable,
                             '' if exponent == 1 else \
                             '^%d'%(self.degree-exponent)))
                    else:
                        cR.append('' if coefficient == 0 else\
                                  '+%s'%(coefficient) if coefficient > 0 else\
                                  '%s'%(coefficient))
            joining = ''.join(["%s"%(r) for r in cR])
            if joining[0] == '+':
                joining = joining[1:]
            return joining
    def __abs__(self):
        return len(self._coefficients)
    def __len__(self):
        return len(self._coefficients)
    @checkTypes
    def __add__(self,other):
        a = copy(self.coefficients)
        b = copy(other.coefficients)
        if self.degree > other.degree:
            diff = self.degree - other.degree
            b = [0]*diff+b
        elif self.degree < other.degree:
            diff = other.degree - self.degree
            a = [0]*diff+a
        s = []
        for i in range(self.degree+1):
            s.append(a[i]+b[i])
        print s
        return Polynomial(s,variable=self.variable)
    def __neg__(self):
        return Polynomial([-a for a in self.coefficients],variable=self.variable)
    def __sub__(self, other):
        return self + (-other)
    def __iter__(self):
        return iter(self._coefficients)
    def iter(self):
        return self.__iter__()
    @checkTypes
    def __mul__(self,other):
        #FIXME: more test needed
        if self.isZero() or other.isZero():
            return Polynomial([],variable=self.variable)
        m = [0]*(self.degree+other.degree+2)
        print("m = %s"%(m))
        a = copy(self.coefficients)
        a.reverse()
        print("a = %s"%(a))
        b = copy(other.coefficients)
        b.reverse()
        print("b = %s"%(b))
        for i in range(len(a)):
            for j in range(len(b)):
                print("m[%d] = a[%d]+b[%d] = %s + %s = %s"%(i+j,i,j,a[i],b[j],m[i+j]))
                m[i+j] += a[i]*b[j]
        m.reverse()
        print("m = %s"%(m))
        return Polynomial(m,variable=self.variable)
    #TODO: multiplicative inverse
    #TODO: division
    #TODO: modular division
