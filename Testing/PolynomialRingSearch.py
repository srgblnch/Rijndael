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
from math import log
from optparse import OptionParser
import psutil
from random import random, randint
import sys
from time import sleep


FIRST_MEM_THRESHOLD = 10.0
SECOND_MEM_THRESHOLD = 19.0


class SimulatedAnheling(_Logger):
    def __init__(self, polynomialRingSize, fieldSize, max_samples,
                 *args, **kwargs):
        super(SimulatedAnheling, self).__init__(*args, **kwargs)
        # --- file log for later audithory
        self._file_suffix = "SimulatedAnheling_ring_%d_coefficients_%d"\
                            % (polynomialRingSize, fieldSize)
        self._log2file = True
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
        nTotal = (2**fieldSize)**polynomialRingSize  # NumberOfPolynomials
        order = int(("%e" % nTotal).split('+')[1])
        # --- Search for a reasonable number of candidates
        #     without an explosion of them.
        self._expectedSamples = int(round(log(nTotal)*order))
        if max_samples is not None and \
                self._expectedSamples > int(max_samples):
            self._expectedSamples = int(max_samples)
        sizeInBits = fieldSize * polynomialRingSize
        sizeInBytes = sizeInBits / 8
        self._hammingGoal = sizeInBits / 2
        if fieldSize == 2 and polynomialRingSize == 2:
            self._deviation = 1
            # --- Force an special case for this very small situation.
        #elif sizeInBytes < 2:
        bar = int(round(log(fieldSize*polynomialRingSize)))
        if bar % 2:
            self._deviation = bar / 2
        else:
            self._deviation = (bar / 2) + 1
        if self._deviation == 0:
            self._deviation = 1
        self._desiredHammingRange = range(self._hammingGoal-self._deviation,
                                          self._hammingGoal+self._deviation+1)
        # --- another range for the coefficients if they need to be checked
        if order < 5:
            self._desiredCoeffHammingRange = None
        else:
            hammingGoal = fieldSize / 2
            bar = int(round(log(fieldSize)))
            if bar % 2:
                deviation = bar / 2
            else:
                deviation = (bar / 2) + 1
            if deviation == 0:
                deviation = 1
            self._desiredCoeffHammingRange = range(hammingGoal-deviation,
                                                   hammingGoal+deviation+1)
        self._info_stream("Preparing a search over a %d degree polynomial "
                          "with %d degree coefficients. The search space has "
                          "%g polynomials. The program will start looking for "
                          "%d candidates within %s hamming weights%s."
                          % (polynomialRingSize, fieldSize, nTotal,
                             self._expectedSamples, self._desiredHammingRange,
                             "" if not self._desiredCoeffHammingRange else
                             " (%s per coefficient)"
                             % self._desiredCoeffHammingRange))
        # --- storage variables
        self._candidatesDct = {}
        self._candidatesLst = []
        self._alreadyTestedPolynomials = []
        # --- simulated anheling new area jump probability
        self._jumpProbability = 0.01
        self._jumpsMade = 0
        self._nearMovements = 0
        # --- about memory usage
        self._memoryPercent = int(psutil.virtual_memory().percent)

    def search(self):
        polynomial = self.__generatePolynomial()
        if self._doPreliminaryTest(polynomial):
            self.__collectForFurtherTest(polynomial)
        while not self.__hasCollectEnough() and not self.__allHasBeenTested():
            if random() > self._jumpProbability:
                polynomial = self.__getNextPolynomial(polynomial)
                if polynomial is None:  # exception to force a space jump
                    polynomial = self.__doJump()
            else:
                polynomial = self.__doJump()
            if self._doPreliminaryTest(polynomial):
                self.__collectForFurtherTest(polynomial)
        winner = self._SecondScreening()
        self._info_stream("Winner polynomial: %s = %s" % (winner, hex(winner)))
        return winner

    def __doJump(self):
        polynomial = self.__generatePolynomial()
        self._jumpsMade += 1
        self._info_stream("Exploring a newer area in the search space "
                          "after %d near movements." % (self._nearMovements))
        self._nearMovements = 0
        return polynomial

    def __generateCoefficient(self):
        '''Generate a random coefficient and, if there is a range of desired
           weights for them, generate some to satisfy this condition.
        '''
        coefficient = self._field(randint(0, 2**self._fieldSize))
        tries = 0
        if self._desiredCoeffHammingRange is not None:
            hammingRange = self._desiredCoeffHammingRange
            while coefficient.hammingWeight not in hammingRange:
                coefficient = self._field(randint(0, 2**self._fieldSize))
                tries += 1
                if tries % 10 == 0:
                    self._debug_stream("Made %d tries "
                                       "to generate random coefficient "
                                       "(%d not in %s)"
                                        % (tries, coefficient.hammingWeight,
                                           hammingRange))
        return coefficient

    def __moveNearCoefficient(self, input, distance):
        coefficient = self._field(input.coefficients + randint(0, distance))
        tries = 0
        if self._desiredCoeffHammingRange is not None:
            while coefficient.hammingWeight not in \
                    self._desiredCoeffHammingRange:
                coefficient = self._field(input.coefficients +
                                          randint(0, distance))
                tries += 1
                if tries % 10 == 0:
                    self._debug_stream("Made %d tries "
                                       "to generate a small change to %s"
                                        % (tries, hex(input)))
        return coefficient

    def __generatePolynomial(self):
        '''Generate a new fresh polynomial at random, checking it hasn't been
           already tested.
        '''
        self._debug_stream("Generate a new random polynomial.")
        polynomialObj = None
        while polynomialObj is None or\
                int(polynomialObj) in self._alreadyTestedPolynomials:
            polynomialLst = [self.__generateCoefficient()
                             for i in range(self._polynomialRingSize)]
            polynomialObj = self._polynomialRing(polynomialLst)
            if int(polynomialObj) in self._alreadyTestedPolynomials:
                self._debug_stream("Discard %s, already tested"
                                   % (hex(polynomialObj)))
            self._debug_stream("Generating a random polynomial candidate: %r"
                               % (hex(polynomialObj)))
        return polynomialObj

    def __getNextPolynomial(self, polynomial):
        self._debug_stream("Move a bit in side the current region of the "
                           "search space")
        oldCoefficients = polynomial.coefficients
        newPolynomial = None
        distance = 1
        while newPolynomial is None:
            newCoefficients = []
            for each in oldCoefficients:
                newCoefficients.append(self.__moveNearCoefficient(each,
                                                                  distance))
                if newCoefficients == oldCoefficients:
                    oldCoefficients.reverse()
                    # FIXME: hackish, do something if nothing has change
                newPolynomial = self._polynomialRing(newCoefficients)
            if int(newPolynomial) in self._alreadyTestedPolynomials:
                self._debug_stream("Discard %s, already tested (%d,%d)"
                                   % (hex(newPolynomial), distance,
                                      len(self._alreadyTestedPolynomials)))
                newPolynomial = None
                distance += 1
                if distance == 10:
                    # --- It is an area of many already tested
                    return None
        self._nearMovements += 1
        return newPolynomial

    def _doPreliminaryTest(self, polynomial):
        if self._memoryPercent != int(psutil.virtual_memory().percent) and\
                psutil.virtual_memory().percent > SECOND_MEM_THRESHOLD:
            self._memoryPercent = int(psutil.virtual_memory().percent)
            self._warning_stream("Memory in use %g, this process uses %g "
                                 "(already tested polynomials %d)"
                                 % (psutil.virtual_memory().percent, 
                                    psutil.Process().memory_percent(),
                                    len(self._alreadyTestedPolynomials)))
        self._alreadyTestedPolynomials.append(int(polynomial))
        if self.__PrefactoryOne(polynomial):
            # if self.__PrefactoryTwo(polynomial):
                if self.__isInvertible(polynomial):
                    inverse = ~polynomial
                    self._alreadyTestedPolynomials.append(int(inverse))
                    if self.__PrefactoryOne(inverse):
                        if self.__PrefactoryTwo(inverse):
                            return True
        return False

    def __PrefactoryOne(self, polynomial):
        if polynomial.hammingWeight in self._desiredHammingRange:
            return True
        self._debug_stream("%s does NOT have the desired hamming weight. (%d)"
                           % (polynomial, polynomial.hammingWeight))
        return False

    def __PrefactoryTwo(self, polynomial):
        # This may not have sense to check the condition on a candidate, 
        # because in the candidate generation (jump or near) this is check.
        # But for its inverse evaluation it is.
        if self._desiredCoeffHammingRange is None:
            return True
        for weight in polynomial.hammingWeightPerCoefficient:
            if weight not in self._desiredCoeffHammingRange:
                self._debug_stream("%s does NOT have the desired hamming "
                                   "weight per coefficient. (%s)"
                                   % (polynomial,
                                      polynomial.hammingWeightPerCoefficient))
                return False
        return True

    def __isInvertible(self, polynomial):
        try:  # if polynomial.isInvertible:
            inverse = ~polynomial
            self._debug_stream("Candidate %s has %s as inverse"
                               % (hex(polynomial), hex(inverse)))
            return True
        except ArithmeticError as e:  # else:
            self._debug_stream("Discard %s, because is not invertible"
                               % (hex(polynomial)))
            return False
        except Exception as e:
            self._error_stream("Discard %s, because an exception %s"
                               % (hex(polynomial), e))
            traceback.print_exc()
            return False

    def __collectForFurtherTest(self, polynomial):
        self._debug_stream("Collecting %s" % polynomial)
        self._candidatesLst.append(polynomial)
        if polynomial.hammingWeight not in self._candidatesDct:
            self._candidatesDct[polynomial.hammingWeight] = []
        self._candidatesDct[polynomial.hammingWeight].append(polynomial)
        self._info_stream("%d candidates collected (%d total checked %d jumps)"
                          % (len(self._candidatesLst),
                             len(self._alreadyTestedPolynomials),
                             self._jumpsMade))
        self.__generatePolynomial()  # do not continue by a near search

    def __hasCollectEnough(self):
        if len(self._candidatesLst) < self._expectedSamples:
            self._debug_stream("%d stored candidates"
                               % len(self._candidatesLst))
            return False
        return True

    def __allHasBeenTested(self):
        nTotal = (2**self._fieldSize)**self._polynomialRingSize
        return nTotal == len(self._alreadyTestedPolynomials)

    # --- TODO: second screening

    def _SecondScreening(self):
        finalists = self._hammingFilter()
        if len(finalists) == 0:
            self._error_stream("NO finalists has passed the second screening!")
            return None
        else:
            finalists = self._coefficientHammingFilter(finalists)
        return finalists

    def _hammingFilter(self):
        if self._hammingGoal in self._candidatesDct:
            finalists = self._candidatesDct[self._hammingGoal]
            self._info_stream("There are %d candidates in the goal "
                              "hamming weight" % len(finalists))
        else:
            finalists = []
            deviation = 0
            while len(finalists) == 0 and deviation < self._deviation:
                deviation += 1
                if self._hammingGoal-deviation in self._candidatesDct:
                    finalists += \
                        self._candidatesDct[self._hammingGoal-deviation]
                if self._hammingGoal+deviation in self._candidatesDct:
                    finalists += \
                        self._candidatesDct[self._hammingGoal+deviation]
            self._info_stream("Taking %d candidates with %d deviation "
                              "for the %d hamming goal"
                              % (len(finalists), deviation, self._hammingGoal))
        return finalists

    def _coefficientHammingFilter(self, candidates):
        dct = {}
        for candidate in candidates:
            hammingLst = candidate.hammingWeightPerCoefficient
            hammingLst.sort()
            if str(hammingLst) not in dct:
                dct[str(hammingLst)] = candidate
        self._info_stream("Candidates hamming weights per coefficients: %s"
                          % dct.keys())
        self._debug_stream("Those candidates are: %s" % dct)
        scores = {}
        for i, combination in enumerate(dct.keys()):
            score = self.__scoreLst(eval(combination))
            if score not in scores:
                scores[score] = []
            scores[score].append(dct[combination])
        self._info_stream("Scoring those hamming weights: %s" % scores)
        scoreKeys = scores.keys()
        scoreKeys.sort()
        candidate = scores[scoreKeys[0]]
        # --- TODO: perhaps there is more than one
        return candidate[0]
    
    def __scoreLst(self, lst):
        lst.sort()
        score = 0
        for i, each in enumerate(lst):
            if i > 0 and each - lst[i-1] != 0:
                score += each - lst[i-1]
        return score


import bz2
from datetime import datetime
import itertools
import gzip
import multiprocessing
import os
from PolynomialsSearch import ActivePool
from shutil import copyfileobj
import traceback


def extractPair(pairStr):
    try:
        first, second = pairStr.split(',')
        return int(first), int(second)
    except Exception as e:
        print("Cannot understand %r as a pair polynomial size,field size"
              % (pairStr))
        sys.exit(-1)


def extractSets(sets):
    try:
        if sets.startswith('[') and sets.endswith(']'):
            lst = eval(sets)
            if type(lst) is not list or\
                    any([type(l) is not list and len(l) == 2 for l in lst]):
                raise Exception("Not understood as a list of pairs")
        elif sets.startswith('{') and sets.endswith('}'):
            lst = []
            dct = eval(sets)
            if type(dct) is not dict:
                raise Exception("Not evaluable as a dictionary")
            for ringdegree in dct:
                if type(dct[ringdegree]) is not list:
                    raise Exception("For ring degree %d, item not evaluable "
                                    "as a list" % ringdegree)
                for coeffdegree in dct[ringdegree]:
                    lst.append([ringdegree, coeffdegree])
        print(lst)
        return lst
    except Exception as e:
        raise Exception("Sets not well understood due to: %s" % e)


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                           "{error,warning,info,debug,trace}.")
    parser.add_option('', "--search-all", action="store_true",
                      help="Do a iterative search for polynomial ring between "
                      "2 and 8, where for each the coefficient field degree "
                      "will be between 2 and 16.")
    parser.add_option('', "--search", type='str',
                      help="Comma separated pair. First number represents the "
                           "degree of the polynomial ring, the second "
                           "represents the extension of the binary field used "
                           "for the coefficients of the polynomial ring.")
    parser.add_option('', "--search-set", type="str",
                      help="Do a iterative search for a set of pair "
                      "of polynomial ring degrees with coefficient field "
                      "degrees. It can receive a list of pair of a dictionary "
                      "with ring degrees with item list of coefficients "
                      "degrees. Remember to write within ''.")
    parser.add_option('', "--parallel-processing", action="store_true",
                      help="Only in search multiple searches, launch each of "
                      "them using multiprocessing.")
    parser.add_option('', "--processors", type="str",
                      help="In case of parallel processing, it can be "
                      "specified the number of parallel jobs to be working. "
                      "With the string 'max' the program will use all the "
                      "available cores. A positive number of them will force "
                      "this number of parallel jobs in execution, and a "
                      "negative number will decrease from the maximum of "
                      "available")
    parser.add_option('', "--max-samples", type="int",
                      help="Tell the algorithm how many samples first "
                      "screening must collect as maximum.")
    

def closeSearch(searcher, logFunc=None, worker=None):
    if searcher.compressedLogfile is None:
        msg = "Compress output to bz2"
        if logFunc:
            logFunc("Worker %d\t%s\n" % (worker, msg))
        else:
            print(msg)
        fileName = searcher.getLogFileName()
        with open(fileName, 'rb') as input:
            with bz2.BZ2File(fileName+'.bz2', 'wb', compresslevel=9) as output:
                copyfileobj(input, output)
        os.remove(fileName)
    elif searcher._file_compression is 'gz':
        msg = "Convert gzip compression to bz2"
        if logFunc:
            logFunc("Worker %d\t%s\n" % (worker, msg))
        else:
            print(msg)
        fileName = searcher.getLogFileName().split('.gz')[0]
        with gzip.open(fileName+'.gz', 'rb') as input:
            with bz2.BZ2File(fileName+'.bz2', 'wb', compresslevel=9) as output:
                copyfileobj(input, output)
        os.remove(fileName+'.gz')
    else:
        msg = "No compression conversion needed. (%s)"\
                % searcher.compressedLogfile
        if logFunc:
            logFunc("Worker %d\t%s\n" % (worker, msg))
        else:
            print(msg)


def singleProcessing(pairs, max_samples, logLevel=_Logger._info):
    results = {}
    for i, j in pairs:
        if i not in results:
            results[i] = {}
        if j not in results[i]:
            results[i][j] = None
        searcher = SimulatedAnheling(i, j, max_samples, logLevel,
                                     file_compression='gz')
        print("Searching for a %d polynomial degree, "
              "with coefficients in an %dth extension of a "
              "characteristic 2 field" % (i, j))
        results[i][j] = searcher.search()
        closeSearch(searcher)
    print("Single processing summary:")
    for v in results.keys():
        print("\tWith %d columns (polynomial ring):" % v)
        for f in results[v].keys():
            result = results[v][f]
            print("\t\tWordsize %d: %s (%r)" % (f, hex(result), result))


def worker(queue, fileName, fLocker, max_samples, logLevel=_Logger._info):
    def write2File(msg):
        with fLocker:
            with open(fileName, 'a') as f:
                f.write("%s\t%s" % (datetime.now().isoformat(),msg))
    id = int(multiprocessing.current_process().name)
    while not queue.empty():
        try:
            i, j = queue.get()
            write2File("Worker %d\tis going to search for pair (%d,%d)\n"
                       % (id, i, j))
            searcher = SimulatedAnheling(i, j, max_samples, logLevel,
                                         file_compression='gz')
            searcher.stdout = False
            result = searcher.search()
            write2File("Worker %d\thas finished the task (%d,%d):"
                       "\t%d degree polynomial ring with %d degree field "
                       "coefficients: %s = %s\n" % (id, i, j, i, j, result,
                                                    hex(result)))
            closeSearch(searcher, write2File, id)
            del searcher
        except Exception as e:
            write2File("** Worker %d\treports an exception for pair (%d,%d): **"
                       "\n\t%s\n" % (id, i, j, e))
    write2File("Worker %d\ttasks queue is empty, ending its execution\n" % (id))


CHECKPERIOD = 60 # a minute


def parallelProcessing(pairs, processors, max_samples, logLevel=_Logger._info):
    def write2File(msg):
        with fLocker:
            with open(fileName, 'a') as f:
                f.write("%s\t%s" % (datetime.now().isoformat(),msg))
    def buildWorker(id):
        return multiprocessing.Process(target=worker, name=str("%d" % (id)),
                                       args=(queue, fileName, fLocker, max_samples,
                                             logLevel))
    try:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = "%s_SimulatedAnheling_ParallelSearch.log" % (now)
        fLocker = multiprocessing.Lock()
        maxParallelprocesses = multiprocessing.cpu_count()
        if processors is None or processors == 'max':
            processors = maxParallelprocesses
        else:
            processors = int(processors)
            if processors < 0:
                processors = maxParallelprocesses + processors
        with open(fileName, 'a') as f:
            write2File("Father\t\tWith %d processors, prepare a set of %d workers\n"
                       % (maxParallelprocesses, processors))
        queue = multiprocessing.Queue()
        for i, j in pairs:
            queue.put([i, j])
        workersLst = []
        for k in range(processors):
            workersLst.append(buildWorker(k))
        for w in workersLst:
            w.start()
        pidsLst = [w.pid for w in workersLst]
        write2File("Father\t\tAll %d workers started. PIDs %s\n"
                   % (len(workersLst), pidsLst))
        memoryPercent = int(psutil.virtual_memory().percent)
        while not queue.empty():
            # --- check if all the workers are alive and working
            while not all([True if pid is not None else False
                       for pid in pidsLst]):
                try:
                    idx = pidsLst.index(None)
                except:
                    pass
                else:
                    deadWorker = workersLst.pop(idx)
                    write2File("Father\t\tWorker %s hasn't PID, replacing it\n"
                               % (deadWorker.name))
                    k += 1
                    newWorker = buildWorker(k)
                    workersLst.append(newWorker)
                    newWorker.start()
                    write2File("Father\t\tNew worker %s replaces %s\n"
                               % (newWorker.name, deadWorker.name))
                    deadWorker.join()
            if int(psutil.virtual_memory().percent) != memoryPercent and\
                    psutil.virtual_memory().percent > FIRST_MEM_THRESHOLD:
                memoryPercent = int(psutil.virtual_memory().percent)
                write2File("Father\t\tWARNING: memory use %g\n"
                           % psutil.virtual_memory().percent)
            sleep(CHECKPERIOD)
            pidsLst = [w.pid for w in workersLst]
        write2File("Father\t\tThe queue is empty\n")
        while len(workersLst) > 0:
            for w in workersLst:
                if not w.is_alive():
                    w.join(1)
                    workersLst.pop(workersLst.index(w))
                    write2File("Father\t\tWorker %s (%d) joined\n"
                               % (w.name, w.pid))
                else:
                    pass  # write2File("Father\t\tWorker %s still working\n"
                          #            % (w.name))
            sleep(CHECKPERIOD)
        write2File("Father\t\tEverything is done.\n")
    except Exception as e:
        print("Uoch! %s" % (e))
        traceback.print_exc()


MAX_RING_DEGREE = 8
MAX_FIELD_DEGREE = 16


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    logLevel = _levelFromMeaning(options.loglevel)
    if options.search is not None:
        polynomialSize, fieldSize = extractPair(options.search)
        searcher = SimulatedAnheling(polynomialSize, fieldSize,
                                     options.max_samples, logLevel)
        result = searcher.search()
        print("summary:")
        print("\tWith %d columns (polynomial ring):" % polynomialSize)
        print("\t\tWordsize %d: %s (%r)" % (fieldSize, hex(result), result))
    elif options.search_set is not None:
        lstOfPairs = extractSets(options.search_set)
        if options.parallel_processing:
            parallelProcessing(lstOfPairs, options.processors, options.max_samples, logLevel)
        else:
            singleProcessing(lstOfPairs, options.max_samples, logLevel)
    elif options.search_all is not None:
        ring_ranges = range(2,MAX_RING_DEGREE+1)
        coefficient_ranges = range(2,MAX_FIELD_DEGREE+1)
        lstOfPairs = list(itertools.product(ring_ranges, coefficient_ranges))
        if options.parallel_processing:
            parallelProcessing(lstOfPairs, options.processors, options.max_samples, logLevel)
        else:
            singleProcessing(lstOfPairs, options.max_samples, logLevel)
    else:
        print("\n\tNo default action, check help to know what can be done.\n")


if __name__ == "__main__":
    main()
