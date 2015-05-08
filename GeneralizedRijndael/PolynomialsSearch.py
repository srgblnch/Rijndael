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

from datetime        import datetime
from Logger          import Logger
from numpy           import array
from optparse        import OptionParser
from Polynomials     import *
from PolynomialsTest import setupLogging


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
       The first element on this list is the polynomials we want.
    '''
    def __init__(self,degree):
        Logger.__init__(self,levelFromMeaning('debug'))
        self._degree = degree
        if self._degree < 3:
            raise ValueError("Out of search range")
        modulo = getBinaryPolynomialRingModulo(degree)
        self._ring = BinaryPolynomialModulo(modulo,variable='z')
        self._candidates = []
        self._nonInvertibles = 0
        self._average = float('NaN')
        self._mu = None
        self._inv_mu = None
        self._nu = None
    
    def search(self):
        self._restriction0()
        self._restriction1()
        self._restriction2()
        self._restriction3()
    
    def _restriction0(self):
        '''
           From all the elements in the binary polynomial ring select the ones 
           that are invertible
        '''
        self.info_stream("R0: fins invertible elements:")
        idx = 2#discard polynomials 0 and 1, start in z
        while idx < 2**self._degree:
            sample = self._ring(idx)
            try:
                inverse = ~sample
            except:
                self._nonInvertibles+=1#discart because is not invertible
            else:
                if not self._candidates.count([inverse,sample]):
                    self._candidates.append([sample,inverse])
                    self.info_stream("\tcandidate found: (%s,%s)"
                                     %(sample,inverse))
                else:
                    self.debug_stream("\tcandidate already in from inverse"\
                                      " (%s)"%(sample))
            idx += 1
        self.info_stream("R0: Found %d candidates and %d non invertible"
                         %(len(self._candidates),self._nonInvertibles))
    
    def _restriction1(self):
        '''
           The invertible elements shall not have itself as inverse
        '''
        self.info_stream("R1: invertible elements shall not have itself "\
                         "as inverse")
        differentInverse = []
        for sample,inverse in self._candidates:
            if sample == inverse:
                self.debug_stream("\tremoving  (%s,%s)"%(sample,inverse))
            else:
                differentInverse.append([sample,inverse])
                self.debug_stream("\tincluding (%s,%s)"%(sample,inverse))
        self._candidates = differentInverse
        self.info_stream("R1: left %d candidates: %s"
                          %(len(self._candidates),self._candidates))
    def _restriction2(self):
        '''
           Evaluate Hamming weights. The goal is to select the ones where the
           accumulated weight of mu candidate and its inverse is closer to 
           the ring degree, and from them the ones where each of them have 
           a weight closer to the half of the ring degree.
        '''
        self.info_stream("R2: balanced hamming weights")
        self._restriction2a()
        self._restriction2b()
        self.info_stream("R2: left %d candidates: %s"
                          %(len(self._candidates),self._candidates))
    
    def _restriction2a(self):
        '''
           Discard the elements in the candidates list with their global 
           hamming weight to far from the ring degree.
        '''
        classification = {}
        for sample,inverse in self._candidates:
            hammingWeight = sample.hammingWeight+inverse.hammingWeight
            if not classification.has_key(hammingWeight):
                classification[hammingWeight] = []
            classification[hammingWeight].append([sample,inverse])
        weights = classification.keys()
        self.debug_stream("\tR2a: weights in the classification: %s"
                          %(weights))
        self._candidates = []
        if weights.count(self._degree):#exact equality
            self._candidates = classification[self._degree]
            self.debug_stream("\t\tfound %d candidates with weight %s"
                              %(len(self._candidates),self._degree))
        else:
            self.debug_stream("\t\tNo candidates with %d"%(self._degree))
            i = 1
            while i<self._degree and not self._candidates:
                indexes = [self._degree-i,self._degree+i]
                for idx in indexes:
                    if classification.has_key(idx):
                        close = classification[idx]
                        self.debug_stream("\t\tfound %d candidates with "\
                                          "weight %d"%(len(close),idx))
                        for candidate in close:
                            self._candidates.append(candidate)
                    else:
                        self.debug_stream("\t\tNo candidates with %d"%(idx))
                i+=1
        self.debug_stream("\tR2a: left %d candidates: %s"
                          %(len(self._candidates),self._candidates))

    def _restriction2b(self):
        '''
           Once the elements in the candidates list have the most closer 
           hamming weight to the degree, a second restricction shall be 
           applied. That is to discard the ones where their individual weight 
           is not close to the half of the ring degree.
        '''
        classification = {}
        for sample,inverse in self._candidates:
            h1 = sample.hammingWeight
            h2 = inverse.hammingWeight
            if not classification.has_key((h1,h2)):
                classification[(h1,h2)] = []
            classification[(h1,h2)].append([sample,inverse])
        weights = classification.keys()
        self.debug_stream("\tR2b: weights classification: %s"%(weights))
        halfdegree = self._degree//2
        self._candidates = []
        idx = (halfdegree,halfdegree)
        if weights.count(idx):
            close = classification[idx]
            self.debug_stream("\t\tfound %d candidates with "\
                              "individual weights %s"
                              %(len(close),idx))
            for candidate in classification[idx]:
                self._candidates.append(candidate)
        else:
            self.debug_stream("\t\tNo candidates with (%d,%d)"
                              %(halfdegree,halfdegree))
            i = 0
            while i<=halfdegree and not self._candidates:
                j = 0
                while j<=halfdegree and not self._candidates:
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
                                self._candidates.append(candidate)
                        else:
                            self.debug_stream("\t\tNo candidates with "\
                                              "(%s,%s)"%(idx[0],idx[1]))
                    j+=1
                i+=1

    def _restriction3(self):
        '''
           Find the nu(z) candidates for each mu candidate, only select the
           triplets with closer hamming weight to (w/2)*3.
           From this subset, check the execution time of them (doing the
           transformation and its inversion) and select the triplet with the
           best timming results.
        '''
        self.debug_stream("R3: Find nu(z) candidates and select triplets with"\
                          " closer hamming weight to (w/2)*3.\n"\
                          "    And from here, the winner is the one with "\
                          "timming results.")
        goalweight = (self._degree/2)*3
        for mu,inv_mu in self._candidates:
            self.debug_stream("\tSearch for nu with (mu(z)=%s,mu^{-1}(z)=%s)"
                              %(mu,inv_mu))
            classified = {}
            for idx in range(2,2**self._degree):
                nu = self._ring(idx)
                #self.debug_stream("\t\ttesting nu(z)=%s"%(nu))
                h = mu.hammingWeight+inv_mu.hammingWeight+nu.hammingWeight
                if not classified.has_key(h):
                    classified[h] = {}
                average = self._fullTestAffineTransformation(mu,nu)
                if average:
                    print("\t\tCandidate (%s,%s,%s) = %f"
                          %(mu,inv_mu,nu,average))
                    if not classified[h].has_key(average):
                        classified[h][average] = []
                    classified[h][average].append([mu,inv_mu,nu])
        finalists = {}
        if classified.has_key(goalweight):
            finalists = classified[goalweight]
            self.info_stream("\tFinalists have goal weight (%d): %s"
                             %(goalweight,finalists))
        else:
            i = 1
            while i<self._degree/2 and not finalists:
                for idx in [goalweight-i,goalweight+i]:
                    if classified.has_key(idx):
                        for average in classified[idx]:
                            finalists[average] = classified[idx][average]
                        self.info_stream("\tFound finalists with weight "\
                                         "%d: %s"%(idx,finalists))
                i+=1
        print("\tFinalists times: %s"%(finalists.keys()))
        averages = finalists.keys(); averages.sort()
        winner = finalists[averages[0]]
        if len(winner) != 1:
            l = ""
            for each in winner:
                l = "%s\t%s\n"%(l,each)
            self.error_stream("***** Found a non unique winner! *****\n%s"%(l))
        else:
            self._average = averages[0]
            self._mu = winner[0][0]
            self._inv_mu = winner[0][1]
            self._nu = winner[0][2]
            self.info_stream("***** The chosen triplet, with mean time %6.3f us "\
                             "is *****\n"\
                             "\tmu(z) = %s = %s\n"\
                             "\tmu^{-1}(z) = %s = %s\n"\
                             "\tnu(z) = %s = %s\n"
                             %(averages[0],
                               self._mu,hex(self._mu),
                               self._inv_mu,hex(self._inv_mu),
                               self._nu,hex(self._nu)))
        

    def _fullTestAffineTransformation(self,mu,nu):
        t_transformations = []
        t_inversions = []
        for i in range(2**self._degree):
            a = self._ring(i)
            b,t = self._affineTransformation(a, mu, nu)
            if a == b or a == -b:
                self.debug_stream("\t\tDiscart %s: fixed or opposite fixed "\
                                  "point found"%(nu))
                return None
            t_transformations.append(t)
            c,t = self._invertAffineTransformation(b, mu, nu)
            if a != c:
                self.warning_stream("\t\tDiscart %s: %s != %s"%(nu,a,c))
                return None
            t_inversions.append(t)
        mean = array(t_transformations).mean() + array(t_inversions).mean()/2
#        self.info_stream("\t\t\tCandidate (%s,%s,%s) with mean time %f"
#                         %(mu,inv_mu,ni,mean))
        return mean
    
    def _affineTransformation(self,a,mu,nu):
        t = datetime.now()
        b = (mu * a) + nu
        #b = (mu.__matrix_product__(a))+nu
        diff_t = datetime.now() -t
        return b,diff_t.microseconds

    def _invertAffineTransformation(self,b,mu,nu):
        t = datetime.now()
        c = ~mu * (b + nu)
        #inv_mu = ~mu
        #c = inv_mu.__matrix_product__(b-nu)
        diff_t = datetime.now() -t
        return c,diff_t.microseconds


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

def doSearch(degree):
    searcher = PolynomialSearch(degree)
    searcher.search()
    when = datetime.now().strftime("%Y%m%d_%H%M%S")
    fileName = "ring_%d_mu_nu_polynomials_%s.dat"\
                                      %(degree,when)
    with open(fileName,'w') as f:
        f.write("average    = %6.3f us\n"\
                "mu(z)      = %s =\t%s\n"\
                "mu^{-1}(z) = %s =\t%s\n"\
                "nu(z)      = %s =\t%s\n"
                %(searcher._average,
                  searcher._mu,    hex(searcher._mu._coefficients),
                  searcher._inv_mu,hex(searcher._inv_mu),
                  searcher._nu,    hex(searcher._nu)))

def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    setupLogging(options.loglevel)
    if options.find_mu_nu_candidates != None:
        doSearch(options.find_mu_nu_candidates)
    elif options.find_all_mu_nu_candidates != None:
        for i in range(3,17):
            doSearch(i)
    else:
        print("\nCommand line parameters required, "\
              "please check -h or --help\n")

if __name__ == "__main__":
    main()

