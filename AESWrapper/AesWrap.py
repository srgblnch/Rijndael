#!/usr/bin/env python2.5

##############################################################################
##
## file: AesWrap.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2009, 2010, 2011, 2012, 2013, 2014 (copyleft)
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

""" Following the rfc3394, this code tries to implement it for testing
    it uses Python Cryptography Toolkit
"""

from Crypto.Cipher import AES
from Crypto.Util import number

class logger:
    def __init__(self,debug):
        self.__logger = {'Silence':0,
                         'Info':1,
                         'Debug':2,
                         'Log':3,
                         'Trace':4}
        self.__debug = self.__logger[debug]
    def info(self,msg):
        if self.__debug >= self.__logger['Info']:
            print "RFC3394.Info:  %s"%msg
            return True
        return False
    def debug(self,msg):
        if self.__debug >= self.__logger['Debug']:
            print "RFC3394.Debug: %s"%msg
            return True
        return False
    def log(self,msg):
        if self.__debug >= self.__logger['Log']:
            print "RFC3394.Log:   %s"%msg
            return True
        return False
    def trace(self,msg):
        if self.__debug >= self.__logger['Trace']:
            print "RFC3394.Trace: %s"%msg
            return True
        return False
#end logger

class AesWrap(logger):
    """ This is a class for objects to encrypt/decrypt data following the rfc3384.
        In the rfc3384 are the specifications of the AES wrap.
    """
    def __init__(self,A_0 = 0xA6A6A6A6A6A6A6A6,debug='Silence'):
        #constant A_0 = IV
        logger.__init__(self,debug)
        self.A_0 = A_0
        self.trace("Object build.")
    #end init

    def __typeCheck(self,element,role):
        if (role == 'P' or role == 'C') and type(element) == list:
            for i in element:
                if not (type(i) == long or type(i) == int):
                    self.info("Ohh! the element %d is not a long! (type:%s)"%(i,type(i)))
                    return False
                elif i > ((2**64)-1):
                    self.info("Ohh! the element %d is not bigger than 64bits!"%i)
                    return False #bigger than 64bits
            return True
        elif role == 'K' and type(element) == str:
            return True
        else:
            self.info("Ohh! __typeCheck() False for the role %s  (type:%s)"%(role,type(element)))
            return False

    def wrap(self,P,KEK):
        """ Implements the alternative algorithm involves indexing.
            @precondition:  Plaintext (n64-bit values {P1,P2,..,Pn}}), and
                            Key KEK
            @postcondition: Ciphertext ((n+1)64-bit values {C0,...,Cn})
        """
        #Becareful the P array starts with 1!!
        #0) intro
        isPlaintext = self.__typeCheck(P,'P')
        isKey = self.__typeCheck(KEK,'K')
        self.info("WRAP precondition: Plaintext %s, key %s"%(isPlaintext,isKey))
        if not isPlaintext or not isKey: raise Exception("Invalid inputs")
        n = len(P)

        #1) Inicialize variables
        A = self.A_0
        #self.R = [None]*n
        R = P
        C = [None]*(n+1)
        self.debug("hexdump P= ["+"".join(["%s,"%(hex(i)) for i in P])+"] (%d elements of 64bits)"%n)
        self.debug("hexdump K=%s"%hex(number.bytes_to_long(KEK)))
        self.__aes = AES.new(KEK)

        self.debug("0,0\tA  %s\t"%(hex(A))+"".join(["R[%d]  %s\t"%(i,hex(R[i])) for i in range(len(R))]))
        #2) Calculate intermediate values
        for j in range(6):# from 0 to 5
            for i in range(1,n+1):#from 1 to n
                B = self.__aes.encrypt(number.long_to_bytes(self.__concatenate(A,R[i-1])))
                self.log("[j=%d,i=%d] B =\t %s = aes(%s,%s|%s)"%(j,i,hex(number.bytes_to_long(B)),hex(number.bytes_to_long(KEK)),hex(A),hex(R[i-1])))
                t = (n*j)+i
                #self.trace("[j=%d,i=%d] t =\t %s"%(j,i,hex(t)))
                A = self.__MSB(64,B) ^ t
                self.log("[j=%d,i=%d] A =\t %s = MSB(64,%s) ^ %s"%(j,i,hex(A),hex(number.bytes_to_long(B)),hex(t)))
                R[i-1] = self.__LSB(64,B)
                self.log("[j=%d,i=%d] R[i] =\t %s = LSB(64,%s)"%(j,i,hex(R[i-1]),hex(number.bytes_to_long(B))))
                self.debug("%d,%d\tA  %s\t"%(j,i,hex(A))+"".join(["R[%d]  %s\t"%(i,hex(R[i])) for i in range(len(R))]))

        #3) Output the result
        C[0] = A
        for i in range(1,n+1):
            C[i] = R[i-1]

        #4) outtro
        isCiphertext = self.__typeCheck(C,'C')
        self.info("WRAP postcondition: Ciphertext %s"%(isCiphertext))
        if not isCiphertext: raise Exception("Invalid inputs")
        self.debug("hexdump C="+"".join(["%s,"%(hex(i)) for i in C])+"(%d elements of 64bits)"%len(C))
        return C
    #end wrap

    def unwrap(self,C,KEK):
        """ Implements the alternative algorithm involves indexing.
            @precondition:  Ciphertext ((n+1)64-bit values {C0,...,Cn}), and
                            Key KEK
            @postcondition: Plaintext (n64-bit values {P1,P2,..,Pn}})
        """
        #0) intro
        isCiphertext = self.__typeCheck(C,'C')
        isKey = self.__typeCheck(KEK,'K')
        self.info("UNWRAP precondition: Ciphertext %s, key %s"%(isCiphertext,isKey))
        if not isCiphertext or not isKey:
            raise Exception("Invalid inputs")
        n = len(C)-1
        
        #1) Initialize variables
        A = C[0]
        R = [None]*n
        for i in range(1,n+1):
            R[i-1] = C[i]
        self.debug("hexdump C= ["+"".join(["%s,"%(hex(i)) for i in C])+"] (%d elements of 64bits)"%(n+1))
        self.debug("hexdump K=%s"%number.bytes_to_long(KEK))
        self.__aes = AES.new(KEK)

        self.debug("0,0\tA  %s\t"%(hex(A))+"".join(["R[%d]  %s\t"%(i,hex(R[i])) for i in range(len(R))]))
        #2) Compute intermediate values
        bar = range(6)
        bar.reverse()
        for j in bar:
            foo = range(1,n+1)
            foo.reverse()
            for i in foo:
                t = (n*j)+i
                B = self.__aes.decrypt(number.long_to_bytes(self.__concatenate(A^t,R[i-1])))
                self.log("[j=%d,i=%d] B =\t %s = aes-1(%s^%s,%s)"%(j,i,hex(number.bytes_to_long(B)),hex(number.bytes_to_long(KEK)),hex(t),hex(R[i-1])))
                A = self.__MSB(64, B)
                self.log("[j=%d,i=%d] A =\t %s = MSB(64,%s)"%(j,i,hex(A),hex(number.bytes_to_long(B))))
                R[i-1] = self.__LSB(64, B)
                self.log("[j=%d,i=%d] R[i] =\t %s = LSB(64,%s)"%(j,i,hex(R[i-1]),hex(number.bytes_to_long(B))))
                self.debug("%d,%d\tA  %s\t"%(j,i,hex(A))+"".join(["R[%d]  %s\t"%(i,hex(R[i])) for i in range(len(R))]))
        #3) Output results
        if not A == self.A_0:
            self.debug("UPS! A_0 = %d"%A)
            self.debug("dump R:\n"+"".join(["%s=%s\n"%(i,R[i]) for i in range(len(R))]))
            raise ValueError,"Integrity check fails, the initial value A_0 not corresponds!"

        #4) outtro
        isPlaintext = self.__typeCheck(R,'P')
        self.info("UNWRAP postcondition: Plaintext %s"%(isPlaintext))
        if not isPlaintext: raise Exception("Invalid inputs")
        self.debug("hexdump P="+"".join(["%s,"%(hex(i)) for i in R])+"(%d elements of 64bits)"%len(R))
        return R
    #end unwrap

    def __concatenate(self,bar,foo):
        self.trace("__concatenate(%s,%s)"%(hex(bar),hex(foo)))
#        bar = number.bignum(bar)
#        foo = number.bignum(foo)
        shift = 64 #shift = number.size(bar)#shift = (((number.size(foo))+8)/4)*4
        barfoo = (bar << shift)+foo
        self.trace("__concatenate: %s (size = %d)"%(hex(barfoo),number.size(barfoo)))
        return barfoo

    def __MSB(self,nbits,input):
        """ Given a bigint as input returns the n most significant bits
        """
        self.trace("__MSB(%s,%s)"%(nbits,hex(number.bytes_to_long(input))))
        bar = number.bytes_to_long(input)
        if nbits > 0:
            foo = bar >> nbits
        else:
            foo = bar
        self.trace("__MSB: %s"%hex(foo))
        return foo
    #end MSB

    def __LSB(self,nbits,input):
        """ Given a bigint as input returns the n less significant bits
        """
        self.trace("__LSB(%s,%s)"%(nbits,hex(number.bytes_to_long(input))))
        bar = number.bytes_to_long(input)
        if nbits > 0:
            mask = (2**nbits)-1
            foo = (bar & mask)
        else:
            foo = input
        self.trace("__LSB: %s"%hex(foo))
        return foo
    #end LSB
#end AesWrap
