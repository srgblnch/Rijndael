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
   This code has been made to provide mu(z), its inverse and nu(z) for a given
   ring size. It must show how they have been selected in order to allow
   reproducibility and algorithm review.
'''

from copy import copy, deepcopy
import csv
from datetime import datetime
from GeneralizedRijndael.Logger import Logger
import multiprocessing
from numpy import array, float64
from optparse import OptionParser
from GeneralizedRijndael.Logger import levelFromMeaning as _levelFromMeaning
from GeneralizedRijndael.Polynomials import *
from PolynomialsTest import setupLogging
from sys import getrecursionlimit, setrecursionlimit
import traceback
from time import clock, time

CEILING = 1e3
ORDER = 10


class TimeMeasurer:
    def __init__(self, *args, **kwargs):
        self._t0 = 0.0

    def start(self):
        self._t0 = self.now

    def stop(self):
        if self._t0 == 0.0:
            raise RuntimeError("First start the timer!")
        now = self.now
        diff = now - self._t0
        if diff < 0:
            print("Negative: %f - %f" % (now, self._t0))
        self._t0 = 0.0
        return diff


class TimeFromDatetime(TimeMeasurer):
    def __init__(self, *args, **kwargs):
        super(TimeFromDatetime, self).__init__(*args, **kwargs)

    @property
    def now(self):
        # Use seconds + microseconds because it a diff falls in two different
        # seconds their diff can be a negative number or, if it takes more than
        # a seconds it will be false.
        now = datetime.now()
        return ((now.hour*60+now.minute)*60+now.second)*1e6+now.microsecond

    @property
    def unit(self):
        return "us"


class TimeFromClock(TimeMeasurer):
    def __init__(self, *args, **kwargs):
        super(TimeFromClock, self).__init__(*args, **kwargs)

    @property
    def now(self):
        return clock()

    @property
    def unit(self):
        return "s"


# class PolynomialEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__str__


class OutputFile(Logger):
    def __init__(self, name, *args, **kwargs):
        super(OutputFile, self).__init__(*args, **kwargs)
        self._file_suffix = name
        self._file_extension = "csv"

    def write(self, incommingdata):
        data = deepcopy(incommingdata)
        fileName = self._when_build.strftime("%Y%m%d_%H%M%S")
        fileName = "%s_%s.%s" % (fileName, self._file_suffix,
                                 self._file_extension)
        with open(fileName, 'a') as outputfile:
            if type(data) == dict:
                w = csv.writer(outputfile)
                row = []
                for key, val in data.items():
                    row.append(key)
                    if type(val) == dict:
                        for subkey, subval in val.items():
                            if type(subkey) == tuple:
                                for e in subkey:
                                    row.append(e)
                            else:
                                row.append(subkey)
                            if type(subval) == list:
                                for triple in subval:
                                    row.append(triple)
                            else:
                                row.append(subval)
                            w.writerow(row)
                            if type(subval) == list:
                                for triple in subval:
                                    row.pop()
                            else:
                                row.pop()
                            if type(subkey) == tuple:
                                for e in subkey:
                                    row.pop()
                            else:
                                row.pop()
                    else:
                        row.append(val)
                        w.writerow([key, val])
                        row.pop()
                    row.pop()
            elif type(data) == list:
                w = csv.writer(outputfile)
                for e in data:
                    w.writerow(e)
            else:
                print type(data)
                outputfile.write(data)


class PolynomialSearch(Logger):
    '''
       Do an exhaustive search in the set of elements of the ring that complain
       with the restrictions:
       0 - the element is invertible in the ring
       1 - the element and its inverse shall be different
       2 - the hamming weight of mu(z) plus mu^{-1}(z)
           closer as possible to $w$. And subset by individuals where its
           weight is closer to $w/2$.
       3 - Find nu(z) candidates, subset by accumulated weight closer to
           $w+w/2$, and sort by calculation time of the transformation (adding
           the transformation and its inverse times).
           See transformation 3 code for more details, but highlight that this
           is not a deterministic calculation. It would have influence if the
           machine where it work has something else to do during the search.
       The first element on this list is the polynomials we want.

       The last constructor argument is set up to parallelise the CPU intensive
       part in restriction 3, when the sboxes shall be tested for all the
       polynomials.
    '''
    def __init__(self, degree, tmeasDateTime=False, inParallel=None,
                 *args, **kwargs):
        super(PolynomialSearch, super).__init__(*args, **kwargs)
        self._degree = degree
        if self._degree < 3:
            raise ValueError("Out of search range")
        self._file_suffix = "PolynomialSearch_%d" % (degree)
        self._log2file = True
        modulo = getBinaryExtensionRingModulo(self._degree)
        self._ring = BinaryExtensionModulo(modulo, variable='z')
        self._std_average = float('NaN')
        self._mu = None
        self._inv_mu = None
        self._nu = None
        self._useDateTime = tmeasDateTime
        self._inParallel = inParallel
        if self._inParallel:
            self._manager = multiprocessing.Manager()
        self._classifiedLock = multiprocessing.Lock()

    def search(self):
        invertibles = self._restriction0()
        OutputFile("ring%d_restriction0_invertibles"
                   % (self._degree).write(invertibles))
        differentInverse = self._restriction1(invertibles)
        OutputFile("ring%d_restriction1_differentInverse"
                   % (self._degree).write(differentInverse))
        goodWeight = self._restriction2(differentInverse)
        OutputFile("ring%d_restriction2_goodWeight"
                   % (self._degree).write(goodWeight))
        self._restriction3(goodWeight)

    def _restriction0(self):
        '''
           From all the elements in the binary polynomial ring select the ones
           that are invertible
        '''
        self._info_stream("R0: fins invertible elements:")
        idx = 2  # discard polynomials 0 and 1, start in z
        _nonInvertibles = 0
        _candidates = []
        while idx < 2**self._degree:
            sample = self._ring(idx)
            try:
                inverse = ~sample
            except:
                _nonInvertibles += 1  # discart because is not invertible
            else:
                if not _candidates.count([inverse, sample]):
                    _candidates.append([sample, inverse])
                    self._info_stream("\tcandidate found: (%s,%s)"
                                      % (sample, inverse))
                else:
                    self._debug_stream("\tcandidate already in from inverse"
                                       " (%s)" % (sample))
            idx += 1
        self._info_stream("R0: Found %d candidates and %d non invertible "
                          "(%d total elements)"
                          % (len(_candidates), _nonInvertibles,
                             2**self._degree))
        return _candidates

    def _restriction1(self, invertibles):
        '''
           The invertible elements shall not have itself as inverse
        '''
        self._info_stream("R1: invertible elements shall not have itself "
                          "as inverse")
        differentInverse = []
        for sample, inverse in invertibles:
            if sample == inverse:
                self._debug_stream("\tremoving  (%s,%s)" % (sample, inverse))
            else:
                differentInverse.append([sample, inverse])
                self._debug_stream("\tincluding (%s,%s)" % (sample, inverse))
        self._info_stream("R1: left %d candidates"
                          % (len(differentInverse)))
        return differentInverse
        # TODO: output a file with the polynomials that has passed this
        #       restriction

    def _restriction2(self, differentInverse):
        '''
           Evaluate Hamming weights. The goal is to select the ones where the
           accumulated weight of mu candidate and its inverse is closer to
           the ring degree, and from them the ones where each of them have
           a weight closer to the half of the ring degree.
        '''
        self._info_stream("R2: balanced hamming weights")
        bestGlobalWeight = self._restriction2a(differentInverse)
        goodWeight = self._restriction2b(bestGlobalWeight)
        self._info_stream("R2: left %d candidates"
                          % (len(goodWeight)))
        # TODO: Output a file with those polynomials and their hamming info
        return goodWeight

    def _restriction2a(self, differentInverse):
        '''
           Discard the elements in the candidates list with their global
           hamming weight to far from the ring degree.
        '''
        classification = {}
        for sample, inverse in differentInverse:
            hammingWeight = sample.hammingWeight+inverse.hammingWeight
            if hammingWeight not in classification:
                classification[hammingWeight] = []
            classification[hammingWeight].append([sample, inverse])
        weights = classification.keys()
        self._info_stream("\tR2a: weights in the classification: %s"
                          % (weights))
        if weights.count(self._degree):  # exact equality
            bestGlobalWeight = classification[self._degree]
            self._debug_stream("\t\tfound %d candidates with weight %s"
                               % (len(bestGlobalWeight), self._degree))
        else:
            bestGlobalWeight = []
            self._warning_stream("\t\tNo candidates with %d" % (self._degree))
            i = 1
            while i < self._degree and not bestGlobalWeight:
                indexes = [self._degree-i, self._degree+i]
                for idx in indexes:
                    if idx in classification:
                        close = classification[idx]
                        self._info_stream("\t\tfound %d candidates with "
                                          "weight %d" % (len(close), idx))
                        for candidate in close:
                            bestGlobalWeight.append(candidate)
                    else:
                        self._warning_stream("\t\tNo candidates with %d"
                                             % (idx))
                i += 1
        self._info_stream("\tR2a: left %d candidates"
                          % (len(bestGlobalWeight)))
        return bestGlobalWeight

    def _restriction2b(self, bestGlobalWeight):
        '''
           Once the elements in the candidates list have the most closer
           hamming weight to the degree, a second restriction shall be
           applied. That is to discard the ones where their individual weight
           is not close to the half of the ring degree.
        '''
        classification = {}
        for sample, inverse in bestGlobalWeight:
            h1 = sample.hammingWeight
            h2 = inverse.hammingWeight
            if (h1, h2) not in classification:
                classification[(h1, h2)] = []
            classification[(h1, h2)].append([sample, inverse])
        weights = classification.keys()
        self._info_stream("\tR2b: weights classification: %s" % (weights))
        return self._classifyByIndividualWeights(classification, weights)

    #####
    # restriction 2 submethods ----
    def _classifyByIndividualWeights(self, classification, weights):
        halfdegree = self._degree//2
        goodWeight = []
        idx = (halfdegree, halfdegree)
        if weights.count(idx):
            close = classification[idx]
            self._debug_stream("\t\tfound %d candidates with "
                               "individual weights %s"
                               % (len(close), idx))
            for candidate in classification[idx]:
                goodWeight.append(candidate)
        else:
            self._debug_stream("\t\tNo candidates with (%d,%d)"
                               % (halfdegree, halfdegree))
            i = 0
            while i <= halfdegree and not goodWeight:
                j = 0
                while j <= halfdegree and not goodWeight:
                    if i == 0 and j == 0:
                        j += 1  # This was already discarted
                    indexes = [(halfdegree-i, halfdegree-j),
                               (halfdegree-i, halfdegree+j),
                               (halfdegree+i, halfdegree-j),
                               (halfdegree+i, halfdegree+j)]
                    for idx in indexes:
                        if weights.count(idx):
                            close = classification[idx]
                            self._debug_stream("\t\tfound %d candidates with "
                                               "individual weights (%s,%s)"
                                               % (len(close), idx[0], idx[1]))
                            for candidate in classification[idx]:
                                goodWeight.append(candidate)
                        else:
                            self._debug_stream("\t\tNo candidates with "
                                               "(%s,%s)" % (idx[0], idx[1]))
                    j += 1
                i += 1
        self._info_stream("\tR2b: left %d candidates" % (len(goodWeight)))
        return goodWeight
    # done restriction 2 submethods ----
    #####

    def _restriction3(self, goodWeight):
        '''
           Find the nu(z) candidates for each mu candidate, only select the
           triplets with closer hamming weight to (w/2)*3.
           From this subset, check the execution time of them (doing the
           transformation and its inversion) and select the triplet with the
           best timming results.
           Best timming results definition can be very fussy. In this case
           it has been defined as:
           - Sort by the standard deviation on the calculation and take the
             set of them that has a minor std.
           - From this subset, if there is more than one element, select the
             one that has used, on average, less time for the calculations.
           NOTE: this is not a deterministic procedure!
        '''
        self._info_stream("R3: Find nu(z) candidates and select triplets "
                          "with closer hamming weight to (w/2)*3.")
        self._info_stream("\tAnd from here, the winner is the one with "
                          "timing results.")
        goalWeight = (self._degree/2)*3
        finalists = {}
        tries = 0
        while len(finalists.keys()) == 0:
            candidates = self._ExpandPairs2Triples(goodWeight, goalWeight)
            classified = self._classifyByCombinedHammingWeight(candidates,
                                                               goalWeight)
            self._info_stream("The %d pairs, has been expanded to %d triples "
                              "to check their computation time."
                              % (len(goodWeight), len(classified)))
            del candidates
            OutputFile("ring%d_restriction3_classified"
                       % (self._degree).write(classified))
            classified = self.__randomCut(classified)
            finalists = self._doTimeMeasurements(classified)
            # If there is no outcome frome the time measurements (because no
            # one of the cut candidates that complains the restriction of fixed
            # points, for example) then try to repeat the collection and cut.
            if len(finalists.keys()) == 0:
                if tries < 10:
                    self._info_stream("With this sampling set it hasn't "
                                      "found finalists. Do a new sampling...")
            # add also a limit on this retries to avoid never ending process.
                else:  # if tries == 10:
                    msg = "After %d samplings no finalists found. "\
                          "No more tries" % (tries)
                    self._warning_stream(msg)
                    raise Exception(msg)
            tries += 1
        del classified
        finalists = self._unflatFinalists(finalists)
        self._selectTheWinner(finalists)

    #####
    # restriction 3 submethods ----
    def _ExpandPairs2Triples(self, goodWeight, goalWeight):
        goalThreshold = goalWeight
        candidates = {}
        total = len(goodWeight)
        for idx, pair in enumerate(goodWeight):
            mu, inv_mu = pair
            percentage = int(float(idx)/total*100)
            for idx in range(2, 2**self._degree):
                nu = self._ring(idx)
                h = mu.hammingWeight+inv_mu.hammingWeight+nu.hammingWeight
                if h in range(goalWeight-goalThreshold,
                              goalWeight+goalThreshold+1):
                    # discard too far weights to save memory
                    if h not in candidates:
                        candidates[h] = []
                    # reduce memory use when collect all the weights
                    # but later they will be needed as polynomials
                    candidates[h].append([mu.coefficients,
                                          inv_mu.coefficients,
                                          nu.coefficients])
            # reduce the dictionary keys if there are better weights
            if goalThreshold > 0:
                distances = []
                for k in candidates:
                    distances.append(abs(goalWeight-k))
                distances.sort()
                self._info_stream("\t\tWeight distances: %s" % (distances))
                if goalThreshold > distances[0]:
                    self._info_stream("\t\tReduce the threshold from %d "
                                      "to %d" % (goalThreshold, distances[0]))
                    if self._degree == 13:
                        # That's a hackish because no finalists found
                        goalThreshold = 1
                    else:
                        goalThreshold = distances[0]
                for k in candidates:
                    if self._degree == 13:
                        # again a hackish for the 13 degree
                        if abs(k-goalWeight) != goalThreshold:
                            x = candidates.pop(k)
                            self._info_stream("\t\tRemoving %d candidates "
                                              "with combined weight %d "
                                              "because there are already "
                                              "some with better weights"
                                              % (len(x), k))
                    else:
                        if abs(k-goalWeight) > goalThreshold:
                            x = candidates.pop(k)
                            self._info_stream("\t\tRemoving %d candidates "
                                              "with combined weight %d "
                                              "because there are already "
                                              "some with better weights"
                                              % (len(x), k))
            items = 0
            for k in candidates.keys():
                # only do the cut if the collected candidates are
                # 1 order of magnitude bigger than the ceiling.
                candidates[k] = self.__randomCut(candidates[k], CEILING*ORDER)
                # There is an if inside to avoid cut if smaller
                items += len(candidates[k])
            self._info_stream("\t[%d%%]Having %d candidates with weights %s"
                              % (percentage, items, candidates.keys()))
        return candidates

    def _classifyByCombinedHammingWeight(self, candidates, goalWeight):
        if goalWeight in candidates:
            classified = candidates[goalWeight]
            self._info_stream("There are %d classified with the goalWeight"
                              % (len(classified)))
        else:
            i = 1
            classified = []
            while i < self._degree/2 and not classified:
                for idx in [goalWeight-i, goalWeight+i]:
                    if idx in candidates:
                        for element in candidates[idx]:
                            classified.append(element)
                        self._info_stream("Added %d classified with combined "
                                          "hamming weight of %d"
                                          % (len(candidates[idx]), idx))
                    else:
                        self._info_stream("No candidates with weight %d"
                                          % (len(candidates[idx])))
        return classified

    def __randomCut(self, sampleSet, limit=CEILING):
        from random import randint
        if len(sampleSet) > limit:
            self._info_stream("Too many elements (%s) in the set, "
                              "doing a random cut" % (len(sampleSet)))
            while len(sampleSet) > limit:
                sampleSet.pop(randint(0, len(sampleSet)-1))
        return sampleSet

    def _doTimeMeasurements(self, classified):
        if len(classified) == 1:
            self._info_stream("With only one classified, avoiding timming "
                              "measures, there is a winner already")
            finalists = {}
            finalists[(None, None)] = classified
        elif self._inParallel:
            finalists = self._manager.list()
            self._makeItParallel(classified, finalists)
        else:
            finalists = {}
            if self._useDateTime:
                tmeasurer = TimeFromDatetime()
            else:
                tmeasurer = TimeFromClock()
            totalElements = len(classified)
            for idx, element in enumerate(classified):
                mu, inv_mu, nu = element
                progress = int(float(idx)/totalElements*100)
                self._testNuCandidate(mu, inv_mu, nu, finalists,
                                      tmeasurer, progress)
        return finalists

    def _unflatFinalists(self, finalists):
        if self._inParallel:
            bar = {}
            for element in finalists:
                std = element[0]
                average = element[1]
                mu = element[2]
                inv_mu = element[3]
                nu = element[4]
                if (std, average) not in bar:
                    bar[(std, average)] = []
                bar[(std, average)].append([mu, inv_mu, nu])
            return bar
        return finalists

    def _selectTheWinner(self, finalists):
        std_average = finalists.keys()
        std_average.sort()
        winner = finalists[std_average[0]]
        if len(winner) != 1:
            l = ""
            for each in winner:
                l = "%s\t%s\n" % (l, each)
            self._error_stream("***** Found a non unique winner! *****\n%s"
                               % (l))
        else:
            self._std_average = std_average[0]
            self._mu = self._ring(winner[0][0])
            self._inv_mu = self._ring(winner[0][1])
            self._nu = self._ring(winner[0][2])
            self._info_stream("***** The chosen triplet, with mean time "
                              "(avg:%s,std:%s) is *****"
                              % (std_average[0][1], std_average[0][0]))
            self._info_stream("\tmu(z) = %s = %s"
                              % (self._mu, hex(self._mu)))
            self._info_stream("\tmu^{-1}(z) = %s = %s"
                              % (self._inv_mu, hex(self._inv_mu)))
            self._info_stream("\tnu(z) = %s = %s" % (self._nu, hex(self._nu)))
            self._info_stream("\tw=%d,h=%d+%d+%d"
                              % (self._degree,
                                 self._mu.hammingWeight,
                                 self._inv_mu.hammingWeight,
                                 self._nu.hammingWeight))
        OutputFile("ring%d_restriction3_winner"
                   % (self._degree).write(winner))

    def _makeItParallel(self, goodCandidates, finalists):
        pool = ActivePool()
        maxParallelprocesses = multiprocessing.cpu_count()
        if self._inParallel > maxParallelprocesses:
            self._warning_stream("Cannot prepare more slots that the available"
                                 "number of cores. Cutting to the maximum.")
            self._inParallel = maxParallelprocesses
        if not self._useDateTime:
            raise EnvironmentError("No support for time.clock in parallel "
                                   "calculation. Use --datetime")
        semaphore = multiprocessing.Semaphore(self._inParallel)
        fLocker = multiprocessing.Lock()
        finish = multiprocessing.Event()
        finish.clear()
        finishedTasks = self._manager.list()
        results = {}
        totalElements = len(goodCandidates)
        jobs = {}
        for idx, element in enumerate(goodCandidates):
            mu, inv_mu, nu = element
            progress = int(float(idx)/totalElements*100)
            jobs[idx] = {'target': self.worker,
                         'name': str(idx),
                         'args': (semaphore, pool, mu, inv_mu, nu, finalists,
                                  progress, finish, finishedTasks)}
        nTasks = len(jobs.keys())
        self._debug_stream("Parallel testing of sboxes candidates. "
                           "%d tasks with %d parallel slots"
                           % (nTasks, self._inParallel))
        # start very many jobs consumes a huge portion of memory
        # then use an event to report that a new job can be launched
        self._debug_stream("Starting %d parallel tasks" % (self._inParallel))
        running = {}
        while len(jobs.keys()) > 0 or len(running.keys()) > 0:
            while len(finishedTasks) > 0:
                j = finishedTasks.pop()
                self._debug_stream("\t\tTask %d has finished "
                                   "(also finished %s)" % (j, finishedTasks))
                running[j].join()
                running.pop(j)
            self._debug_stream("\t\tPrepare to launch %d tasks"
                               % (self._inParallel-len(running.keys())))
            while len(jobs.keys()) > 0 and \
                    len(running.keys()) < self._inParallel:
                i = jobs.keys()[0]
                self._debug_stream("\t\tPreparing to launch task %d "
                                   "(running %s)" % (i, running.keys()))
                running[i] = self.launchNewTask(i, jobs)
                jobs.pop(i)
            self._debug_stream("\t\tWait to task finish: %s"
                               % (running.keys()))
            if len(running.keys()) > 0:
                finish.wait()
                finish.clear()

    def launchNewTask(self, i, jobs):
        job = multiprocessing.Process(target=jobs[i]['target'],
                                      name=jobs[i]['name'],
                                      args=jobs[i]['args'])
        self._debug_stream("\t\tLaunching task %d" % (i))
        job.start()
        return job

    def worker(self, flow, pool, mu, inv_mu, nu, finalists, progress,
               hasFinish, finishedTasks):
        tmeasurer = TimeFromDatetime()
        with flow:
            pid = int(multiprocessing.current_process().name)
            pool.makeActive("%s" % (pid))
            self._testNuCandidate(mu, inv_mu, nu, finalists, tmeasurer,
                                  progress)
            pool.makeInactive("%s" % (pid))
            finishedTasks.append(pid)
            hasFinish.set()

    def _testNuCandidate(self, mu, inv_mu, nu, finalists, tmeasurer, progress):
        mu = self._ring(mu)
        inv_mu = self._ring(inv_mu)
        nu = self._ring(nu)
        try:
            average, std = self._fullTestAffineTransformation(mu, nu,
                                                              tmeasurer)
        except ArithmeticError as e:
            self._warning_stream("\t[%d%%]Discarted (%s,%s,%s): %s"
                                 % (progress, mu, inv_mu, nu, e))
            return
        if average:
            self._info_stream("\t[%d%%]Candidate (%s,%s,%s)"
                              " = %f (std %g)"
                              % (progress, mu, inv_mu, nu, average, std))
            with self._classifiedLock:
                candidate = [mu.coefficients,
                             inv_mu.coefficients,
                             nu.coefficients]
                if self._inParallel:
                    element = [std, average] + candidate
                    finalists.append(element)
                else:
                    if (std, average) not in finalists:
                        finalists[(std, average)] = []
                    finalists[(std, average)].append(candidate)

    def _fullTestAffineTransformation(self, mu, nu, tmeasurer):
        """
        """
        try:
            t_ring = []
            t_matrix = []
            for i in range(2**self._degree):
                a = self._ring(i)
                b, tr, bm, tm = self._affineTransformation(a, mu, nu,
                                                           tmeasurer)
                if a == b:
                    raise ArithmeticError("Fixed point found")
                elif a == -b:
                    raise ArithmeticError("Opposite fixed point found")
                    self._debug_stream("\t\tDiscart %s: fixed or opposite "
                                       "fixed point found" % (nu))
                    raise ArithmeticError("")
                t_ring.append(tr)
                t_matrix.append(tm)
                c, tr, cm, tm = self._invertAffineTransformation(b, bm, mu, nu,
                                                                 tmeasurer)
                if a != c:
                    raise AssertionError("%s != %s" % (a, c))
                t_ring.append(tr)
                t_matrix.append(tm)
            t_ring = array(t_ring)
            t_matrix = array(t_matrix)
            # Usually is smallest the time using ring view
            results = t_ring
            return results.mean(), results.std()
        except ArithmeticError as e:
            self._debug_stream("\t\tDiscart %s: %s" % (nu, e))
            raise e
        except AssertionError as e:
            self._warning_stream("\t\tDiscart %s: %s" % (nu, e))
            raise e
        except Exception as e:
            self._error_stream("Exception in full test of affine "
                               "transformation for mu(z)=%s,nu(z)=%s: %s"
                               % (mu, nu, e))
            import traceback
            traceback.print_exc()
            return None, None

    def _affineTransformation(self, a, mu, nu, tmeasurer):
        tmeasurer.start()
        b = (mu * a) + nu
        diff_r = tmeasurer.stop()
        tmeasurer.start()
        bm = (mu.__matrix_product__(a))+nu
        diff_m = tmeasurer.stop()
        return b, diff_r, bm, diff_m

    def _invertAffineTransformation(self, b, bm, mu, nu, tmeasurer):
        tmeasurer.start()
        c = ~mu * (b + nu)
        diff_r = tmeasurer.stop()
        inv_mu = ~mu
        tmeasurer.start()
        cm = inv_mu.__matrix_product__(b-nu)
        diff_m = tmeasurer.stop()
        return c, diff_r, cm, diff_m
    # done restriction 3 submethods ----
    #####


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--loglevel", type="str",
                      help="output prints log level: "
                           "{error,warning,info,debug,trace}")
    parser.add_option('', "--find-mu-nu-candidates", type='int',
                      help="Given a size of a ring (in bits) return the pair"
                           "of mu(z) and nu(z) that satisfies the "
                           "restrictions.")
    parser.add_option('', "--find-all-mu-nu-candidates", action="store_true",
                      help="Loops over all expected rings to find mus and nus")
    parser.add_option('', "--datetime", action="store_true",
                      help="By default the time meter is from time.clock(), "
                           "but can be cahnged to use datetime library to "
                           "measure.")
    parser.add_option('', "--parallel-processing", action="store_true",
                      help="When find candidates for many rings, "
                           "do it in parallel")
    parser.add_option('', "--parallel-sboxes", type='int',
                      help="How many parallel processes used to check the "
                           "sboxes restrictions with in a ring search"
                           "do it in parallel")


def doSearch(degree, tmeasDateTime, loglevel=Logger._info,
             res=None, inParallel=None):
    try:
        searcher = PolynomialSearch(degree, tmeasDateTime, loglevel,
                                    inParallel)
        searcher.search()
        if type(res) == dict:
            res = {degree, [searcher._mu, searcher._nu]}
        return copy(searcher._mu), copy(searcher._nu)
    except Exception as e:
        try:
            searcher._error_stream("Fatal error during search: %s" % (e))
            import traceback
            trace = traceback.format_exc()
            searcher._error_stream("Traceback:\n%s" % (trace))
        except:
            fName = datetime.now().strftime("%Y%m%d_%H%M%S")+".log"
            with open(fName, 'a') as f:
                f.write("fatal (%d): %s" % (degree, e))


class ActivePool(object):
    """
    """
    def __init__(self):
        super(ActivePool, self).__init__()
        self._manager = multiprocessing.Manager()
        self._active = self._manager.list()
        self._lock = multiprocessing.Lock()
        self._results = {}  # self._manager.dict()

    def makeActive(self, name):
        with self._lock:
            self._active.append(name)

    def makeInactive(self, name):
        with self._lock:
            self._active.remove(name)

    def __str__(self):
        with self._lock:
            return str(self._active)

    def saveResults(self, key, value):
        with self._lock:
            self._results[key] = value
            print("Saving results in ActivePool, they are: %s"
                  % (self._results))


def worker(_lock, pool, tmeasDateTime, fName, fLocker, logLevel=Logger._info):
    id = int(multiprocessing.current_process().name)
    with _lock:
        pool.makeActive("%s" % (id))
        print('Worker %d running. Total Now running: %s' % (id, str(pool)))
        # - a
#        pool._results[id] = (id**2,id**3)
#        import time,random
#        time.sleep(id*random.random())
        # - b
        mu, nu = doSearch(id, tmeasDateTime, logLevel)
        print("answer[%d]: mu=%s nu=%s" % (id, mu, nu))
        pool.saveResults(id, [mu, nu])
        # - end
        print("At %d worker, results are: %s" % (id, pool._results))
        pool.makeInactive("%s" % (id))
        with fLocker:
            with open(fName, 'a') as f:
                msg = "ring %d:\tmu(z)=%30s\t(%s)\tnu(z)=%30s\t(%s)\n"\
                      % (id, mu, hex(mu), nu, hex(nu))
                print(msg)
                f.write(msg)

MIN_RING = 3
MAX_RING = 16


def makeItParallel(measCk, fName, logLevel=Logger._info):
    pool = ActivePool()
    maxParallelprocesses = multiprocessing.cpu_count()
    semaphore = multiprocessing.Semaphore(maxParallelprocesses)
    fLocker = multiprocessing.Lock()
    results = {}
    jobs = [
        multiprocessing.Process(target=worker,
                                name=str(i),
                                args=(semaphore, pool, measCk, fName,
                                      fLocker, logLevel))
        for i in range(MAX_RING, MIN_RING-1, -1)
        ]

    for j in jobs:
        print('On start, running: %s' % (str(pool)))
        j.start()

    for j in jobs:
        j.join()
        print('Finish, running: %s' % (str(pool)))
    print("At the end: %s" % (pool._results))


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    setupLogging(options.loglevel)
    logLevel = _levelFromMeaning(options.loglevel)
    if options.find_mu_nu_candidates is not None:
        print("in parallel: %s" % (options.parallel_sboxes))
        doSearch(options.find_mu_nu_candidates, options.datetime,
                 logLevel, inParallel=options.parallel_sboxes)
    elif options.find_all_mu_nu_candidates is not None:
        results = {}
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fName = "%s_all_mu_nu_from_%d_to_%d.log" % (now, MIN_RING, MAX_RING)
        if options.parallel_processing:
            try:
                makeItParallel(options.clock_timer, fName, logLevel)
            except Exception as e:
                print("Uoch! %s" % (e))
                traceback.print_exc()
        else:
            for i in range(MIN_RING, MAX_RING+1):
                try:
                    results[i] = doSearch(i, options.datetime, logLevel)
                    with open(fName, 'a') as f:
                        f.write("ring %d:\tmu(z)=%30s\t(%s)\tnu(z)=%30s\t(%s)"
                                "\n" % (i, results[i][0], hex(results[i][0]),
                                        results[i][1], hex(results[i][1])))
                except Exception as e:
                    print("Uoch! %s" % (e))
                    traceback.print_exc()
    else:
        print("\nCommand line parameters required, "
              "please check -h or --help\n")

if __name__ == "__main__":
    main()
