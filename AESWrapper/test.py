#!/usr/bin/env python2.5

##############################################################################
##
## file: GeneralizedRijndael.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2011, 2012, 2013, 2014 (copyleft)
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

from AesWrap import *
import sys
import os, getopt
from datasamples import *
from Crypto.Util import number

def help():
    print "\nThis code has been written as a test for the AESWrap and AESUnwrap methods from the rfc3394"
    print "Usage:"
    print "\t [python] test.py [--wrap|unwrap|both] [--data=n --key=m][--[info|debug|trace]]\n"
    print "Parameters description:"
    print "\tActions"
    print "\t\twrap:\t\tDo the test only on the encryption operation."
    print "\t\tunwrap:\t\tDo the test for decryption operation."
    print "\t\tboth:\t\tFirst encrypt and then decrypt the result."
    print "\tLengths: always both parameters"
    print "\t\tdata=n:\t\tSelect this length for the data."
    print "\t\tkey=m:\t\tSelect this length for the key."
    print "\t\t\t\tCombinations:"
    print "\t\t\t\t\tdata 128 -> key 128|192|256"
    print "\t\t\t\t\tdata 192 -> key     192|256"
    print "\t\t\t\t\tdata 256 -> key         256"
    print "\tLogger levels"
    print "\t\tinfo:\t\tSome tags of the procedure on the stdout."
    print "\t\tdebug:\t\tDebugging information on the stdout."
    print "\t\tlog:\t\tShow some information about the algorithm steps."
    print "\t\ttrace:\t\tTagging about what is executed, step by step.\n"

def long2str(input,fixLength=True):
    
    foo = ""
    if type(input) == list:
        #print "long2str: input "+"".join(["%s,"%(hex(i)) for i in input])
        for i in input:
            foo = foo+number.long_to_bytes(i)
    else:
        #print "long2str: input %s"%hex(input)
        foo = number.long_to_bytes(input)
    if fixLength:
        while (len(foo) not in [16,24,32]) and len(foo) <= 32:
            foo = '\x00'+foo
    #print "long2str: ouput %s (len %d)"%(repr(foo),len(foo))
    return foo

def wrap(sample):
    bar = AesWrap(debug=debug)
    #prepare the input data:
    P = sample['Input'][1:]
    KEK = long2str(sample['KEK'])
    R = bar.wrap(P,KEK)
    C = sample['Output']
    print "Compare with the specs: data = %d, key = %d"%(sample['len'][0],sample['len'][1])
    if len(C) == len(R):
        for i in range(len(C)):
            print "%s ?= %s"%(hex(R[i]),hex(C[i]))
    else:
        print "len(R)=%d, len(C)=%d"%(len(R),len(C))
        print "R = %s"%R
        print "C = %s"%C
    return R

def unwrap(sample):
    bar = AesWrap(debug=debug)
    #prepare the input data:
    C = sample['Output']
    KEK = long2str(sample['KEK'])
    R = bar.unwrap(C,KEK)
    P = sample['Input'][1:]
    print "Compare with the specs: data = %d, key = %d"%(sample['len'][0],sample['len'][1])
    if len(P) == len(R):
        for i in range(len(P)):
            print "%s ?= %s"%(hex(R[i]),hex(P[i]))
    else:
        print "len(R)=%d, len(P)=%d"%(len(R),len(P))
        print "R = %s"%R
        print "P = %s"%P
    return R

if __name__ == "__main__":
    try:
        opt_pairs, pargs = getopt.getopt(sys.argv[1:], "h", ['help','info','debug','log','trace',
                                                             'wrap','unwrap','both',
                                                             'data=','key='])
    except getopt.GetoptError, e:
        print str(e)
        sys.exit()

    opts = map(lambda x : x[0], opt_pairs)

    debug = 'Silence'
    if opts.count('-h') or opts.count('--help'):
        help()
        sys.exit()
    if opts.count('--info'):
        debug='Info'
    if opts.count('--debug'):
        debug='Debug'
    if opts.count('--log'):
        debug='Log'
    if opts.count('--trace'):
        debug='Trace'

    if opts.count('--data') and opts.count('--key'):
        data = int(opt_pairs[opts.index('--data')][1])
        key = int(opt_pairs[opts.index('--key')][1])
        samples = []
        for foo in structs:
            if foo['len'][0] == data and foo['len'][1] == key:
                samples = [foo]
        if samples == []:
            print "Length not recognized. Try with the combinations:"
            print "data 128 -> key 128|192|256"
            print "data 192 -> key     192|256"
            print "data 256 -> key         256"
    else:
        samples = structs

    if opts.count('--wrap'):
        for foo in samples:
            wrap(foo)
    elif opts.count('--unwrap'):
        for foo in samples:
            unwrap(foo)
    elif opts.count('--both'):
        for foo in samples:
            R = wrap(foo)
            foo['Output'] = R
            unwrap(foo)