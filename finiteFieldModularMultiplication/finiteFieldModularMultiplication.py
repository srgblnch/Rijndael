##############################################################################
##
## file: finiteFieldModularMultiplication.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2011, 2012 (copyleft)
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

binlen = lambda x: len(bin(x))-2

class FiniteFieldModularMultiplication:
    def __init__(self): pass
    def multiplication(self,a,b,m=0x1b):
        '''multiplication of polynomials modulo an irreductible pylinomial of 
           field's degree. Over F_{2^8} this polynomial is 
           m(x) = x^8+x^4+x^3+x+1
        '''
        #Polynomial multiplication
        c = 0
        for i in range(binlen(b)):#FIXME: get the number of bits of a number 
            if b & (1<<i):#for each 1 in b
                c ^= (a<<i)#add a to the partial
        #print "a * b = %s * %s = %s = c"%(hex(a),hex(b),hex(c))
        #Polynomial reduction
        if (binlen(c)<binlen(m)):#no reduction need
            return c
        #print("c = %s mod %s"%(hex(c),hex(m)))
        if not (binlen(c)==binlen(m)):
            r = (c >> (binlen(c)-binlen(m)))#r in step 0
            c_ = bin(c)[2+binlen(m):]#c_ contain the rest of the bits of c that will be used in division
        else:
            r = c ^ m
            c_ = ""
        while len(c_) > 0:
            while binlen(r) < binlen(m) and len(c_) > 0:
                r = (r<<1) | int(c_[0])
                c_ = c_[1:]
            r^=m
        #print "c mod m = %s mod %s = %s = r"%(hex(c),hex(m),hex(r))
        if binlen(r) == binlen(m): return r ^ m
        return r

    def multiplicationRecursive(self,a,b,m=0x11b):
        b_ = b
        xor = []
        a_i = [a]
        for i in range(binlen(b)):
            if b_&1:
                xor.append(a_i[len(a_i)-1])
            b_ >>= 1
            a_i.append(self.xtime(a_i[len(a_i)-1], m))
        r = 0
        for x in xor:
            r ^= x
        return r

    def xtime(self,a,m=0x11b):
        a <<= 1
        if a & (1<<binlen(m)-1): a ^= m
        return a

def main():
    bar = FiniteFieldModularMultiplication()
    a = 0x57
    b = 0x83
    m = 0x11B#0b100011011
    
    #{57}*{13} = {57}*({01)^{02}^{10}) = {57}^{ae}^{07} = {fe}
    a2 = bar.xtime(a,m)
    a2_ = bar.multiplication(a,0x2,m)
    print("%s*0x2=%s\txtime=%s\t(should be 0xae)"%(hex(a),hex(a2_),hex(a2)))
    a4 = bar.xtime(a2,m)
    a4_ = bar.multiplication(a,0x4,m)
    print("%s*0x4=%s\txtime=%s\t(should be 0x47)"%(hex(a),hex(a4_),hex(a4)))
    a8 = bar.xtime(a4,m)
    a8_ = bar.multiplication(a,0x8,m)
    print("%s*0x8=%s\txtime=%s\t(should be 0x8e)"%(hex(a),hex(a8_),hex(a8)))
    a10 = bar.xtime(a8,m)
    a10_ = bar.multiplication(a,0x10,m)
    print("%s*0x10=%s\txtime=%s\t(should be 0x07)"%(hex(a),hex(a10_),hex(a10)))
    a13 = a ^ a2 ^ a10
    a13_ = bar.multiplication(a,0x13,m)
    print("%s*0x13=%s\txtime=%s\t(should be 0xfe)"%(hex(a),hex(a13_),hex(a13)))
    
    #compare the two algorithms
    for b in range(2,0x14):
        foo = bar.multiplication(a,b,m)
        rec = bar.multiplicationRecursive(a,b,m)
        print "a * b = %s * %s =\t%s ?= %s\t(mod %s)"%(hex(a),hex(b),hex(foo),hex(rec),hex(m))
        #if not foo == rec: break

if __name__ == "__main__":
    main()
