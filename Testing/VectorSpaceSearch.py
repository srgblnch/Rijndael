#!/usr/bin/env python
#---- licence header
##############################################################################
##
## file: VectorSpaceSearch.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2016 (copyleft)
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

'''
   This code has been made to provide c(x), its inverse and d(x) for a given 
   vector length (ring size). It must show how they have been selected in order to allow 
   reproducibility and algorithm review.
'''
from GeneralizedRijndael.Logger import Logger as _Logger
from GeneralizedRijndael.Logger import levelFromMeaning as _levelFromMeaning
from GeneralizedRijndael.Polynomials import *
from optparse import OptionParser
from PolynomialsTest import setupLogging
from random import random,randint
import sys

class SimulatedAnheling(_Logger):
    def __init__(self,vectorSpaceSize,fieldSize,logLevel=_Logger._info):
        super(SimulatedAnheling,self).__init__(logLevel)
        self._fieldSize = fieldSize
        fieldModulo = getBinaryExtensionFieldModulo(fieldSize)
        self._field = BinaryExtensionModulo(fieldModulo,variable='z',
                                            loglevel=logLevel)
        self._info_stream("Build the field modulo m(z)=%s"%(self._field(0).modulo))
        self._vectorSpaceSize = vectorSpaceSize
        vectorModulo = "x^%d+1"%(vectorSpaceSize)
        self._vectorSpace = \
        VectorSpaceModulo(vectorModulo,self._field,loglevel=logLevel)
        self._info_stream("Build the vector space modulo l(x)=%s"%(self._vectorSpace([0]*self._vectorSpaceSize).modulo))
        self._vectorCandidate = None
        self._testedVectors = []#FIXME: improve the way this is check
    
    def search(self):
        self.__generateVector()
        while not self.__test():
            self._debug_stream("Discard %s"%(self._vectorCandidate))
            if random() > 0.1:#get a closer candidate
                self.__getNextVector()
            else:#jump to a different area of the search space
                self.__generateVector()
            self._debug_stream("Testing: %s"%(self._vectorCandidate))
        self._info_stream("Winner: %s"%(self._vectorCandidate))
        self._info_stream("Hex notation: %s"%(hex(self._vectorCandidate)))
        self._info_stream("%d tested vectors"%(len(self._testedVectors)))
        return self._vectorCandidate

    def __generateVector(self):
        while self._vectorCandidate == None or \
              self._vectorCandidate in self._testedVectors:
            self._vectorCandidate =  self._vectorSpace(\
                                [self._field(randint(0,2**self._fieldSize)) 
                                for i in range(self._vectorSpaceSize)])
            self._debug_stream("Generating a random vector: %r"
                              %(self._vectorCandidate))

    def __getNextVector(self):
        #TODO
        self.__generateVector()

    def __test(self):
        #TODO:
        self._debug_stream("%d tested vectors"%(len(self._testedVectors)))
        self._testedVectors.append(self._vectorCandidate)
        return random() > 0.9

def extractPair(pairStr):
    try:
        first,second = pairStr.split(',')
        return int(first),int(second)
    except Exception as e:
        print("Cannot understand %r as a pair vector size,field size"%(pairStr))
        sys.exit(-1)

def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('',"--loglevel",type="str",
                      help="output prints log level: "\
                                            "{error,warning,info,debug,trace}")
    parser.add_option('',"--search",type='str',
                      help="Comma separated pair. First the number of "\
                      "elements in the vector space, followed with the "\
                      "size of the coeficients binary field.")
    parser.add_option('',"--search-all",action="store_true",
                      help="Do a iterative search for vector spaces between "\
                      "2 and 8, with on each iterate with fields between "\
                      "2 and 16")
    
def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    setupLogging(options.loglevel)
    if options.search != None:
        vectorSize,fieldSize = extractPair(options.search)
        searcher = SimulatedAnheling(vectorSize,fieldSize)
        searcher.search()
    elif options.search_all != None:
        for v in range(2,8):
            for f in range(2,16):
                print("Searching for a %d vector space size, "\
                      "with coefficients in an %dth extension of a "\
                      "characteristic 2 field"%(v,f))
                searcher = SimulatedAnheling(v,f)
                searcher.search()
    else:
        print("\n\tNo default action, check help to know what can be done.\n")


if __name__ == "__main__":
    main()
