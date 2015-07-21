#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: PolynomialsSearch.py
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2014,2015 (copyleft)
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
   This code has been made to provide mu(z), its inverse and nu(z) for a given 
   ring size. It must show how they have been selected in order to allow 
   reproducibility and algorithm review.
'''

from copy import copy
from datetime import datetime
from Logger import Logger
import multiprocessing
from numpy import array
from optparse import OptionParser
from Polynomials import *
from PolynomialsTest import setupLogging
import traceback
from time import clock,time

class TimeMeasurer:
    def __init__(self):
        self._t0 = 0.0

    def start(self):
        self._t0 = self.now

    def stop(self):
        if self._t0 == 0.0:
            raise RuntimeError("First start the timer!")
        now = self.now
        diff = now - self._t0
        if diff < 0:
            print("Negative: %f - %f"%(now,self._t0))
        self._t0 = 0.0
        return diff


class TimeFromDatetime(TimeMeasurer):
    def __init__(self):
        #super(TimeFromDatetime,self).__init__()
        TimeMeasurer.__init__(self)

    @property
    def now(self):
        #Use seconds + microseconds because it a diff falls in two different 
        #seconds their diff can be a negative number or, if it takes more than
        #a seconds it will be false.
        now = datetime.now()
        return now.second*1e6 + now.microsecond

    @property
    def unit(self):
        return "us"


class TimeFromClock(TimeMeasurer):
    def __init__(self):
        #super(TimeFromClock,self).__init__()
        TimeMeasurer.__init__(self)

    @property
    def now(self):
        return clock()

    @property
    def unit(self):
        return "s"


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
    '''
    def __init__(self,degree,tmeasDateTime=False,logLevel=Logger.info):
        Logger.__init__(self,logLevel)
        self._degree = degree
        if self._degree < 3:
            raise ValueError("Out of search range")
        self._file_suffix = "PolynomialSearch_%d"%degree
        self._log2file = True
        modulo = getBinaryPolynomialRingModulo(self._degree)
        self._ring = BinaryPolynomialModulo(modulo,variable='z')
        self._std_average = float('NaN')
        self._mu = None
        self._inv_mu = None
        self._nu = None
        if tmeasDateTime:
            self._tmeasurer = TimeFromDatetime()
        else:
            self._tmeasurer = TimeFromClock()
    
    def search(self):
        invertibles = self._restriction0()
        differentInverse = self._restriction1(invertibles)
        goodWeight = self._restriction2(differentInverse)
        self._restriction3(goodWeight)
    
    def _restriction0(self):
        '''
           From all the elements in the binary polynomial ring select the ones 
           that are invertible
        '''
        self.info_stream("R0: fins invertible elements:")
        idx = 2#discard polynomials 0 and 1, start in z
        _nonInvertibles = 0
        _candidates = []
        while idx < 2**self._degree:
            sample = self._ring(idx)
            try:
                inverse = ~sample
            except:
                _nonInvertibles+=1#discart because is not invertible
            else:
                if not _candidates.count([inverse,sample]):
                    _candidates.append([sample,inverse])
                    self.info_stream("\tcandidate found: (%s,%s)"
                                     %(sample,inverse))
                else:
                    self.debug_stream("\tcandidate already in from inverse"\
                                      " (%s)"%(sample))
            idx += 1
        self.info_stream("R0: Found %d candidates and %d non invertible "\
                         "(%d total elements)"
                         %(len(_candidates),_nonInvertibles,
                           2**self._degree))
        return _candidates
    
    def _restriction1(self,invertibles):
        '''
           The invertible elements shall not have itself as inverse
        '''
        self.info_stream("R1: invertible elements shall not have itself "\
                         "as inverse")
        differentInverse = []
        for sample,inverse in invertibles:
            if sample == inverse:
                self.debug_stream("\tremoving  (%s,%s)"%(sample,inverse))
            else:
                differentInverse.append([sample,inverse])
                self.debug_stream("\tincluding (%s,%s)"%(sample,inverse))
        self.info_stream("R1: left %d candidates"
                          %(len(differentInverse)))
        return differentInverse
        #TODO: output a file with the polynomials that has passed this 
        #      restriction
    def _restriction2(self,differentInverse):
        '''
           Evaluate Hamming weights. The goal is to select the ones where the
           accumulated weight of mu candidate and its inverse is closer to 
           the ring degree, and from them the ones where each of them have 
           a weight closer to the half of the ring degree.
        '''
        self.info_stream("R2: balanced hamming weights")
        bestGlobalWeight = self._restriction2a(differentInverse)
        goodWeight = self._restriction2b(bestGlobalWeight)
        self.info_stream("R2: left %d candidates"
                          %(len(goodWeight)))
        #TODO: Output a file with those polynomials and their hamming info
        return goodWeight
    
    def _restriction2a(self,differentInverse):
        '''
           Discard the elements in the candidates list with their global 
           hamming weight to far from the ring degree.
        '''
        classification = {}
        for sample,inverse in differentInverse:
            hammingWeight = sample.hammingWeight+inverse.hammingWeight
            if not classification.has_key(hammingWeight):
                classification[hammingWeight] = []
            classification[hammingWeight].append([sample,inverse])
        weights = classification.keys()
        self.info_stream("\tR2a: weights in the classification: %s"
                          %(weights))
        if weights.count(self._degree):#exact equality
            bestGlobalWeight = classification[self._degree]
            self.debug_stream("\t\tfound %d candidates with weight %s"
                              %(len(bestGlobalWeight),self._degree))
        else:
            bestGlobalWeight = []
            self.warning_stream("\t\tNo candidates with %d"%(self._degree))
            i = 1
            while i<self._degree and not bestGlobalWeight:
                indexes = [self._degree-i,self._degree+i]
                for idx in indexes:
                    if classification.has_key(idx):
                        close = classification[idx]
                        self.info_stream("\t\tfound %d candidates with "\
                                          "weight %d"%(len(close),idx))
                        for candidate in close:
                            bestGlobalWeight.append(candidate)
                    else:
                        self.warning_stream("\t\tNo candidates with %d"%(idx))
                i+=1
        self.info_stream("\tR2a: left %d candidates"
                          %(len(bestGlobalWeight)))
        return bestGlobalWeight

    def _restriction2b(self,bestGlobalWeight):
        '''
           Once the elements in the candidates list have the most closer 
           hamming weight to the degree, a second restricction shall be 
           applied. That is to discard the ones where their individual weight 
           is not close to the half of the ring degree.
        '''
        classification = {}
        for sample,inverse in bestGlobalWeight:
            h1 = sample.hammingWeight
            h2 = inverse.hammingWeight
            if not classification.has_key((h1,h2)):
                classification[(h1,h2)] = []
            classification[(h1,h2)].append([sample,inverse])
        weights = classification.keys()
        self.info_stream("\tR2b: weights classification: %s"%(weights))
        halfdegree = self._degree//2
        goodWeight = []
        idx = (halfdegree,halfdegree)
        if weights.count(idx):
            close = classification[idx]
            self.debug_stream("\t\tfound %d candidates with "\
                              "individual weights %s"
                              %(len(close),idx))
            for candidate in classification[idx]:
                goodWeight.append(candidate)
        else:
            self.debug_stream("\t\tNo candidates with (%d,%d)"
                              %(halfdegree,halfdegree))
            i = 0
            while i<=halfdegree and not goodWeight:
                j = 0
                while j<=halfdegree and not goodWeight:
                    if i == 0 and j == 0:
                        j+=1#This was already discarted
                    indexes = [(halfdegree-i,halfdegree-j),
                               (halfdegree-i,halfdegree+j),
                               (halfdegree+i,halfdegree-j),
                               (halfdegree+i,halfdegree+j)]
                    
                    for idx in indexes:
                        if weights.count(idx):
                            close = classification[idx]
                            self.debug_stream("\t\tfound %d candidates with "\
                                              "individual weights (%s,%s)"
                                              %(len(close),idx[0],idx[1]))
                            for candidate in classification[idx]:
                                goodWeight.append(candidate)
                        else:
                            self.debug_stream("\t\tNo candidates with "\
                                              "(%s,%s)"%(idx[0],idx[1]))
                    j+=1
                i+=1
        self.info_stream("\tR2b: left %d candidates"
                          %(len(goodWeight)))
        return goodWeight

    def _restriction3(self,goodWeight):
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
        self.info_stream("R3: Find nu(z) candidates and select triplets "\
                          "with closer hamming weight to (w/2)*3.")
        self.info_stream("\tAnd from here, the winner is the one with "\
                         "timming results.")
        goalWeight = (self._degree/2)*3
        classified = {}
        for mu,inv_mu in goodWeight:
            self.info_stream("\tSearch for nu with (mu(z)=%s,mu^{-1}(z)=%s)"
                              %(mu,inv_mu))
            for idx in range(2,2**self._degree):
                nu = self._ring(idx)
                #self.debug_stream("\t\ttesting nu(z)=%s"%(nu))
                h = mu.hammingWeight+inv_mu.hammingWeight+nu.hammingWeight
                average,std = self._fullTestAffineTransformation(mu,nu)
                if average:
                    self.info_stream("\t\tCandidate (%s,%s,%s) = %f (std %g)"
                                      %(mu,inv_mu,nu,average,std))
                    if not classified.has_key(h):
                        classified[h] = {}
                    if not classified[h].has_key((std,average)):
                        classified[h][(std,average)] = []
                    classified[h][(std,average)].append([mu,inv_mu,nu])
        finalists = {}
        if classified.has_key(goalWeight) and len(classified[goalWeight]) > 0:
            finalists = classified[goalWeight]
            self.info_stream("\tFound %d finalists with the goal weight (%d)"
                             %(len(finalists.keys()),goalWeight))
            #TODO: output file with the finalist information
            for k in finalists.keys():
                self.info_stream("\t\tavg:%g, std:%g:\t%s"
                                %(k[1],k[0],finalists[k]))
        else:
            i = 1
            while i<self._degree/2 and not finalists:
                for idx in [goalWeight-i,goalWeight+i]:
                    if classified.has_key(idx):
                        for std,average in classified[idx]:
                            finalists[(std,average)] = \
                                classified[idx][(std,average)]
                        self.info_stream("\tFound %d finalists with weight "\
                                         "%d"%(len(finalists.keys()),idx))
                        #TODO: output file with the finalist information
                        for k in finalists.keys():
                            self.info_stream("\t\tavg:%g, std:%g:\t%s"
                                              %(k[1],k[0],finalists[k]))
                i+=1
        std_average = finalists.keys(); std_average.sort()
        winner = finalists[std_average[0]]
        if len(winner) != 1:
            l = ""
            for each in winner:
                l = "%s\t%s\n"%(l,each)
            self.error_stream("***** Found a non unique winner! *****\n%s"%(l))
        else:
            self._std_average = std_average[0]
            self._mu = winner[0][0]
            self._inv_mu = winner[0][1]
            self._nu = winner[0][2]
            self.info_stream("***** The chosen triplet, with mean time "\
                             "(avg:%s,std:%s) %s is *****"
                             %(std_average[0][1],std_average[0][0],
                               self._tmeasurer.unit))
            self.info_stream("\tmu(z) = %s = %s"
                             %(self._mu,hex(self._mu)))
            self.info_stream("\tmu^{-1}(z) = %s = %s"
                             %(self._inv_mu,hex(self._inv_mu)))
            self.info_stream("\tnu(z) = %s = %s"%(self._nu,hex(self._nu)))
            self.info_stream("\tw=%d,h=%d+%d+%d"
                             %(self._degree,
                               self._mu.hammingWeight,
                               self._inv_mu.hammingWeight,
                               self._nu.hammingWeight))
        

    def _fullTestAffineTransformation(self,mu,nu):
        """
        """
        try:
            t_ring = []
            t_matrix = []
            for i in range(2**self._degree):
                a = self._ring(i)
                b,tr,bm,tm = self._affineTransformation(a,mu,nu)
                if a == b or a == -b:
                    self.debug_stream("\t\tDiscart %s: fixed or opposite fixed "\
                                      "point found"%(nu))
                    return None,None
                t_ring.append(tr)
                t_matrix.append(tm)
                c,tr,cm,tm = self._invertAffineTransformation(b,bm,mu,nu)
                if a != c:
                    self.warning_stream("\t\tDiscart %s: %s != %s"%(nu,a,c))
                    return None,None
                t_ring.append(tr)
                t_matrix.append(tm)
            t_ring = array(t_ring)
            t_matrix = array(t_matrix)
            
            #Usually is smallest the time using ring view
            results = t_ring
            #results = t_matrix
            
            return results.mean(),results.std()
        except Exception,e:
            self.error_stream("Exception in full test of affine "\
                              "transformation for mu(z)=%s,nu(z)=%s: %s"
                              %(mu,nu,e))
            import traceback
            traceback.print_exc()
            return None,None
    
    def _affineTransformation(self,a,mu,nu):
        self._tmeasurer.start()
        b = (mu * a) + nu
        diff_r = self._tmeasurer.stop()
        self._tmeasurer.start()
        bm = (mu.__matrix_product__(a))+nu
        diff_m = self._tmeasurer.stop()
        return b,diff_r,bm,diff_m

    def _invertAffineTransformation(self,b,bm,mu,nu):
        self._tmeasurer.start()
        c = ~mu * (b + nu)
        diff_r = self._tmeasurer.stop()
        inv_mu = ~mu
        self._tmeasurer.start()
        cm = inv_mu.__matrix_product__(b-nu)
        diff_m = self._tmeasurer.stop()
        return c,diff_r,cm,diff_m

def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('',"--loglevel",type="str",
                      help="output prints log level: "\
                                            "{error,warning,info,debug,trace}")
    parser.add_option('',"--find-mu-nu-candidates",type='int',
                      help="Given a size of a ring (in bits) return the pair"\
                      "of mu(z) and nu(z) that satisfies the restrictions.")
    parser.add_option('',"--find-all-mu-nu-candidates",action="store_true",
                      help="Loops over all expected rings to find mus and nus")
    parser.add_option('',"--datetime",action="store_true",
                      help="By default the time meter is from time.clock(), "\
                      "but can be cahnged to use datetime library to measure.")
    parser.add_option('',"--parallel-processing",action="store_true",
                      help="When find candidates for many rings, "\
                      "do it in parallel")

def doSearch(degree,tmeasDateTime,loglevel=Logger.info,res=None):
    try:
        searcher = PolynomialSearch(degree,tmeasDateTime,loglevel)
        searcher.search()
        if type(res) == dict:
            res = {degree,[searcher._mu,searcher._nu]}
        return copy(searcher._mu),copy(searcher._nu)
    except Exception,e:
        try:
            searcher.error_stream("Fatal error during search: %s"%(e))
            import traceback
            traceback.print_exc()
        except:
            fName = datetime.now().strftime("%Y%m%d_%H%M%S")+".log"
            with open(fName,"a") as f:
                f.write("fatal (%d): %s"%(degree,e))


class ActivePool(object):
    """
    """
    def __init__(self):
        super(ActivePool, self).__init__()
        self._manager = multiprocessing.Manager()
        self._active = self._manager.list()
        self._lock = multiprocessing.Lock()
        self._results = {}#self._manager.dict()
    def makeActive(self, name):
        with self._lock:
            self._active.append(name)
    def makeInactive(self, name):
        with self._lock:
            self._active.remove(name)
    def __str__(self):
        with self._lock:
            return str(self._active)
    def saveResults(self,key,value):
        with self._lock:
            self._results[key] = value
            print("Saving results in ActivePool, they are: %s"%(self._results))

def worker(_lock, pool, tmeasDateTime,fName,fLocker,logLevel=Logger.info):
    id = int(multiprocessing.current_process().name)
    with _lock:
        pool.makeActive("%s"%id)
        print('Worker %d running. Total Now running: %s'%(id,str(pool)))
        ## - a
#        pool._results[id] = (id**2,id**3)
#        import time,random
#        time.sleep(id*random.random())
        ## - b
        mu,nu = doSearch(id,tmeasDateTime,logLevel)
        print("answer[%d]: mu=%s nu=%s"%(id,mu,nu))
        pool.saveResults(id,[mu,nu])
        ## - end
        print("At %d worker, results are: %s"%(id,pool._results))
        pool.makeInactive("%s"%id)
        with fLocker:
            with open(fName,"a") as f:
                msg = "ring %d:\tmu(z)=%30s\t(%s)\tnu(z)=%30s\t(%s)\n"\
                      %(id,mu,hex(mu),nu,hex(nu))
                print(msg)
                f.write(msg)

MIN_RING = 3
MAX_RING = 16



def makeItParallel(measCk,fName,logLevel=Logger.info):
    pool = ActivePool()
    nParallelprocesses = multiprocessing.cpu_count()
    semaphore = multiprocessing.Semaphore(nParallelprocesses)
    fLocker = multiprocessing.Lock()
    results = {}
    jobs = [
        multiprocessing.Process(target=worker, 
                                name=str(i), 
                                args=(semaphore, pool, measCk,fName,
                                      fLocker,logLevel))
        for i in range(MAX_RING,MIN_RING-1,-1)
        ]

    for j in jobs:
        print('On start, running: %s'%str(pool))
        j.start()

    for j in jobs:
        j.join()
        print('Finish, running: %s'%str(pool))
    print("At the end: %s"%pool._results)


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    setupLogging(options.loglevel)
    logLevel = levelFromMeaning(options.loglevel)
    if options.find_mu_nu_candidates != None:
        doSearch(options.find_mu_nu_candidates,options.datetime,logLevel)
    elif options.find_all_mu_nu_candidates != None:
        results = {}
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        fName = "%s_all_mu_nu_from_%d_to_%d.log"%(now,MIN_RING,MAX_RING)
        if options.parallel_processing:
            try:
                makeItParallel(options.clock_timer,fName,logLevel)
            except Exception,e:
                print("Uoch! %s"%(e))
                traceback.print_exc()
        else:
            for i in range(MIN_RING,MAX_RING+1):
                try:
                    results[i] = doSearch(i,options.datetime,logLevel)
                    with open(fName,"a") as f:
                        f.write("ring %d:\tmu(z)=%30s\t(%s)\tnu(z)=%30s\t(%s)\n"
                                %(i,results[i][0],hex(results[i][0]),
                                  results[i][1],hex(results[i][1])))
                except Exception,e:
                    print("Uoch! %s"%(e))
                    traceback.print_exc()
    else:
        print("\nCommand line parameters required, "\
              "please check -h or --help\n")

if __name__ == "__main__":
    main()

