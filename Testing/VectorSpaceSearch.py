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
__copyright__ = "Copyright 2015 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

'''
   This code has been made to provide c(x), its inverse and d(x) for a given
   vector length (ring size). It must show how they have been selected in
   order to allow reproducibility and algorithm review.
'''

from GeneralizedRijndael.Logger import Logger as _Logger
from GeneralizedRijndael.Logger import levelFromMeaning as _levelFromMeaning
from GeneralizedRijndael.Polynomials import *
from optparse import OptionParser
from random import random, randint
import sys

from time import sleep  # FIXME: to be removed


class SimulatedAnheling(_Logger):
    def __init__(self, vectorSpaceSize, fieldSize, *args, **kwargs):
        super(SimulatedAnheling, self).__init__(*args, **kwargs)
        self._fieldSize = fieldSize
        fieldModulo = getBinaryExtensionFieldModulo(fieldSize)
        self._field = BinaryExtensionModulo(fieldModulo, variable='z',
                                            loglevel=self.logLevel)
        self._info_stream("Build the field modulo m(z)=%s"
                          % (self._field(0).modulo))
        self._vectorSpaceSize = vectorSpaceSize
        vectorModulo = "x^%d+1" % (vectorSpaceSize)
        self._vectorSpace = VectorSpaceModulo(vectorModulo, self._field,
                                              loglevel=self.logLevel)
        zeroVector = [0]*self._vectorSpaceSize
        self._info_stream("Build the vector space modulo l(x)=%s"
                          % (self._vectorSpace(zeroVector).modulo))
        self._vectorCandidate = None
        self._testedVectors = []  # FIXME: improve the way this is checked
        self._testNextVSGenNew = 0.99

    def search(self):
        inTheArea = 0
        self.__generateVector()
        while not self.__test():
            self._debug_stream("Discard %s" % (self._vectorCandidate))
            if random() < self._testNextVSGenNew: 
                self.__getNextVector()
                # get a closer candidate
                self._testNextVSGenNew -= 0.01
                # reduce this probability to stay in this area
                inTheArea += 1
            else:
                self._info_stream("After %d nears, jump to a newer area"
                                  % inTheArea)
                self.__generateVector()
                # jump to a different area of the search space
                self._testNextVSGenNew = 0.99
                # reset this probability of the region search
                inTheArea = 0
            self._debug_stream("Testing: %s" % (hex(self._vectorCandidate)))
        self._info_stream("Winner: %s" % (self._vectorCandidate))
        self._info_stream("Hex notation: %s" % (hex(self._vectorCandidate)))
        self._info_stream("%d tested vectors" % (len(self._testedVectors)))
        return self._vectorCandidate

    def __generateVector(self):
        '''Generate a new fresh vector at random, checking it hasn't been
           already tested.
        '''
        self._debug_stream("Jump to a newer area in the search space.")
        while self._vectorCandidate is None or \
                self._vectorCandidate in self._testedVectors:
            vector = [self._field(randint(0, 2**self._fieldSize))
                      for i in range(self._vectorSpaceSize)]
            self._vectorCandidate = self._vectorSpace(vector)
            self._debug_stream("Generating a random vector: %r"
                               % (self._vectorCandidate))

    def __getNextVector(self):
        self._debug_stream("Move a bit in side the current region of the "
                           "search space")
        oldCandidate = self._vectorCandidate
        oldCoefficients = oldCandidate.coefficients
        newCandidate = None
        while newCandidate == None:
            newCoefficients = []
            for each in oldCoefficients:
                value = each.coefficients
                newCoefficients.append(self._field(value+randint(0,1)))
                newCandidate = self._vectorSpace(newCoefficients)
            if newCandidate in self._testedVectors:
                self._debug_stream("Discard next, already tested")
                newCandidate = None
        self._vectorCandidate = newCandidate

    def __test(self):
        # self._debug_stream("%d tested vectors" % (len(self._testedVectors)))
        # TODO: Check if it is invertible
        # TODO: What other requerements can be made for those candidates?
        self._testedVectors.append(self._vectorCandidate)
        return random() > 0.995
        # FIXME: once there are decision constrains for the candidates,
        #        remove this random choser


def extractPair(pairStr):
    try:
        first, second = pairStr.split(',')
        return int(first), int(second)
    except Exception as e:
        print("Cannot understand %r as a pair vector size,field size"
              % (pairStr))
        sys.exit(-1)


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                           "{error,warning,info,debug,trace}")
    parser.add_option('', "--search", type='str',
                      help="Comma separated pair. First the number of "
                           "elements in the vector space, followed with the "
                           "size of the coeficients binary field.")
    parser.add_option('', "--search-all", action="store_true",
                      help="Do a iterative search for vector spaces between "
                           "2 and 8, with on each iterate with fields between "
                           "2 and 16")


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    logLevel = _levelFromMeaning(options.loglevel)
    if options.search is not None:
        vectorSize, fieldSize = extractPair(options.search)
        searcher = SimulatedAnheling(vectorSize, fieldSize, logLevel)
        searcher.search()
    elif options.search_all is not None:
        results = {}
        for v in range(2, 8):
            if v not in results:
                results[v] = {}
            for f in range(2, 16):
                print("Searching for a %d vector space size, "
                      "with coefficients in an %dth extension of a "
                      "characteristic 2 field" % (v, f))
                searcher = SimulatedAnheling(v, f)
                results[v][f] = searcher.search()
        print("summary:")
        for v in results.keys():
            print("\tWith %d columns (vector space):" % v)
            for f in results[v].keys():
                print("\t\tWordsize %d: %s" % (f, hex(results[v][f])))
    else:
        print("\n\tNo default action, check help to know what can be done.\n")


if __name__ == "__main__":
    main()
