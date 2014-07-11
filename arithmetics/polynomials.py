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

class Polynomial:
    def __init__(self,value,variable='x'):
        '''Polynomial defined by coefficients in a field or a ring.
           The coefficients are described in a list where the first is biggest.
           Example: polynomials.Polynomial([1,0,2,3],variable='z')
           means: z^3 + 2z^1 + 3
        '''
        self._variable = variable
        if type(value) == list and len(value)>0:
            self._coefficients = value
            #remove null elements on the left side coefficients
            while self._coefficients[0] == 0:
                self._coefficients.pop(0)
            #check all remaining elements have same integer type
            for i in range(len(self._coefficients)):
                if type(self._coefficients[0]) != type(self._coefficients[i]):
                    raise ValueError("All the polynomial coefficients must "\
                                     "be the same type")
        elif type(value) == Polynomial:
            self._coefficients = value.coefficients
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
    def checkTypes(self,other):
        if not self.variable == other.variable:
            raise EnvironmentError("Uncompatible polynomials")
        #TODO: check if their coefficients have the same type
    def __repr__(self):
        if self.isZero():
            return '0'
        else:
            cR = [] #coefficients representations list
            #FIXME: review this naming
            for exponent,coefficient in enumerate(self._coefficients):
                if not coefficient == 0:
                    if self.degree-exponent > 0:
                        cR.append("(%s%s^%d)"
                           %(coefficient if coefficient != 1 else '',
                             self._variable,self.degree-exponent))
                    else:
                        cR.append('%s'%(coefficient))
            return '+'.join(["%s"%(r) for r in cR])
    def __abs__(self):
        return len(self._coefficients)
    def __len__(self):
        return len(self._coefficients)
    #@checkTypes#FIXME: decorator with arguments
    def __add__(self,other):
        self.checkTypes(other)
        a = self.coefficients
        b = other.coefficients
        if self.degree > other.degree:
            diff = self.degree - other.degree
            b = [0]*diff+b
        elif self.degree < other.degree:
            diff = other.degree - self.degree
            a = [0]*diff+a
        s = []
        for i in range(self.degree+1):
            s.append(a[i]+b[i])
        return Polynomial(s,variable=self.variable)
    def __neg__(self):
        return Polynomial([-a for a in self.coefficients],variable=self.variable)
    def __sub__(self, other):
        return self + (-other)
    def __iter__(self):
        return iter(self._coefficients)
    def iter(self):
        return self.__iter__()
    #@checkTypes
    def __mul__(self,other):
        self.checkTypes(other)
        if self.isZero() or other.isZero():
            return Polynomial([],variable=self.variable)
        m = [0]*(self.degree+other.degree+2)
        print("m = %s"%(m))
        a = self.coefficients
        a.reverse()
        print("a = %s"%(a))
        b = self.coefficients
        b.reverse()
        print("b = %s"%(b))
        for i in range(len(a)):
            for j in range(len(b)):
                print("m[%d] = a[%d]+b[%d] = %s + %s = %s"%(i+j,i,j,a[i],b[j],m[i+j]))
                m[i+j] += a[i]*b[j]
        print("m = %s"%(m))
        return Polynomial(m,variable=self.variable)
