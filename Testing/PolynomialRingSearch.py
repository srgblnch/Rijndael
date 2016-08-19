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
   polynomial ring degree. It must show how they have been selected in
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
    def __init__(self, polynomialRingSize, fieldSize, *args, **kwargs):
        super(SimulatedAnheling, self).__init__(*args, **kwargs)
        # --- prepare
        self._fieldSize = fieldSize
        fieldModulo = getBinaryExtensionFieldModulo(fieldSize)
        self._field = BinaryExtensionModulo(fieldModulo, variable='z',
                                            loglevel=self.logLevel)
        self._info_stream("Build the field modulo m(z)=%s"
                          % (self._field(0).modulo))
        self._polynomialRingSize = polynomialRingSize
        polynomialRingModulo = "x^%d+1" % (polynomialRingSize)
        self._polynomialRing = PolynomialRingModulo(polynomialRingModulo,
                                                    self._field,
                                                    loglevel=self.logLevel)
        zero = [0]*self._polynomialRingSize
        self._info_stream("Build the polynomial ring modulo l(x)=%s"
                          % (self._polynomialRing(zero).modulo))
        totalNumberOfPolynomials = (2**fieldSize)**polynomialRingSize
        order = int(("%e"%totalNumberOfPolynomials).split('+')[1])
        if order < 4:
            self._expectedSamples = float("1e%d"%(order-1))
        else:
            self._expectedSamples = 1e4
        # --- Search for a reasonable number of candidates
        #     without an explosion of them.
        self._info_stream("With %d degree polynomials with %d degree "
                          "coefficients, there are %d possible candidates."
                          "This program with try to collect first %d "
                          "candidates"
                          % (polynomialRingSize, fieldSize,
                             totalNumberOfPolynomials, self._expectedSamples))
        # --- storage variables
        self._polynomialCandidate = None
        self._candidatesLst = []
        self._alreadyTestedPolynomials = []
        # FIXME: improve the way to check that someone
        #        was already random generated
        self._testNextpolynomialRingGenNew = 0.99

    def search(self):
        inTheArea = 0
        self.__generatePolynomial()
        while not self.__hasCollectEnough():
            self._debug_stream("Discard %s" % (self._polynomialCandidate))
            if random() < self._testNextpolynomialRingGenNew:
                self.__getNextPolynomial()
                # get a closer candidate
                self._testNextpolynomialRingGenNew -= 0.01
                # reduce this probability to stay in this area
                inTheArea += 1
                if self.__preliminarTest():
                    self.__collectForFurtherTest()
            else:
                self._info_stream("After %d nears, jump to a newer area"
                                  % inTheArea)
                self.__generatePolynomial()
                # jump to a different area of the search space
                self._testNextpolynomialRingGenNew = 0.99
                # reset this probability of the region search
                inTheArea = 0
                if self.__preliminarTest():
                    self.__collectForFurtherTest()
            self._debug_stream("Testing: %s"
                               % (hex(self._polynomialCandidate)))
        self._info_stream("Winner: %s with its inverse %s"
                          % (self._polynomialCandidate,
                             ~self._polynomialCandidate))
        self._info_stream("Hex notation: %s and %s"
                          % (hex(self._polynomialCandidate),
                             hex(~self._polynomialCandidate)))
        self._info_stream("%d tested polynomialss"
                          % (len(self._alreadyTestedPolynomials)))
        return self._polynomialCandidate

    def __generatePolynomial(self):
        '''Generate a new fresh polynomial at random, checking it hasn't been
           already tested.
        '''
        self._debug_stream("Jump to a newer area in the search space.")
        while self._polynomialCandidate is None or \
                self._polynomialCandidate in self._alreadyTestedPolynomials:
            polynomial = [self._field(randint(0, 2**self._fieldSize))
                          for i in range(self._polynomialRingSize)]
            candidate = self._polynomialRing(polynomial)
            self._info_stream("Generating a random polynomial: %r"
                              % (hex(candidate)))
            if candidate in self._alreadyTestedPolynomials:
                self._debug_stream("Discard %s, already tested"
                                   % (hex(candidate)))
            elif self.__isInvertible(candidate):
                self._polynomialCandidate = candidate

    def __getNextPolynomial(self):
        self._debug_stream("Move a bit in side the current region of the "
                           "search space")
        oldCandidate = self._polynomialCandidate
        oldCoefficients = oldCandidate.coefficients
        self._polynomialCandidate = None
        while self._polynomialCandidate is None:
            newCoefficients = []
            for each in oldCoefficients:
                value = each.coefficients
                newCoefficients.append(self._field(value+randint(0, 1)))
                newCandidate = self._polynomialRing(newCoefficients)
            if newCandidate in self._alreadyTestedPolynomials:
                self._debug_stream("Discard %s, already tested"
                                   % (hex(newCandidate)))
            elif self.__isInvertible(newCandidate):
                self._info_stream("%s can be a candidate"
                                  % (hex(newCandidate)))
                self._polynomialCandidate = newCandidate

    def __isInvertible(self, candidate):
        try:
            inv = ~candidate
            self._debug_stream("Candidate %s has %s as inverse"
                               % (hex(candidate), hex(inv)))
            return True
        except:
            self._debug_stream("Discard %s, because is not invertible"
                               % (hex(candidate)))
            return False

    def __hasCollectEnough(self):
        if len(self._candidatesLst) < self._expectedSamples:
            self._info_stream("%d stored candidates" % len(self._candidatesLst))
            return False
        return True

    def __preliminarTest(self):
        # self._debug_stream("%d tested polynomials"
        #                    % (len(self._alreadyTestedPolynomials)))
        # TODO: What other requerements can be made for those candidates?
        self._alreadyTestedPolynomials.append(self._polynomialCandidate)
        return random() > 0.9
        # FIXME: once there are decision constrains for the candidates,
        #        remove this random choser

    def __collectForFurtherTest(self):
        self._candidatesLst.append(self._polynomialCandidate)
        self.__generatePolynomial()  # do not continue by a near search


def extractPair(pairStr):
    try:
        first, second = pairStr.split(',')
        return int(first), int(second)
    except Exception as e:
        print("Cannot understand %r as a pair polynomial size,field size"
              % (pairStr))
        sys.exit(-1)


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                           "{error,warning,info,debug,trace}")
    parser.add_option('', "--search", type='str',
                      help="Comma separated pair. First number represents the"
                           "degree of the polynomial ring, the second "
                           "represents the extension of the binary field used"
                           "for the coefficients of the polynomial ring.")
    parser.add_option('', "--search-all", action="store_true",
                      help="Do a iterative search for polynomial ring between "
                           "2 and 8, with on each iterate with fields between "
                           "2 and 16")


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    logLevel = _levelFromMeaning(options.loglevel)
    if options.search is not None:
        polynomialSize, fieldSize = extractPair(options.search)
        searcher = SimulatedAnheling(polynomialSize, fieldSize, logLevel)
        searcher.search()
    elif options.search_all is not None:
        results = {}
        for v in range(2, 8):
            if v not in results:
                results[v] = {}
            for f in range(2, 16):
                print("Searching for a %d polynomial degree, "
                      "with coefficients in an %dth extension of a "
                      "characteristic 2 field" % (v, f))
                searcher = SimulatedAnheling(v, f)
                results[v][f] = searcher.search()
        print("summary:")
        for v in results.keys():
            print("\tWith %d columns (polynomial ring):" % v)
            for f in results[v].keys():
                print("\t\tWordsize %d: %s" % (f, hex(results[v][f])))
    else:
        print("\n\tNo default action, check help to know what can be done.\n")


if __name__ == "__main__":
    main()
