#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: GeneralizedRijndael.pyx
##
## developers history & copyleft: Sergi Blanch-Torne
##
## Copyright 2014 (copyleft)
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

import Logger
import KeyExpansion

class GeneralizedRijndael(Logger.Logger):
    def __init__(self,key,
                 nRounds=10,nRows=4,nColumns=4,wordSize=8,#stardard aes
                 nKeyWords=None,
                 loglevel=Logger.Logger.info):
        Logger.Logger.__init__(self,loglevel)
        self.__nRounds=nRounds#Num of encryption rounds {10,12,14}
        self.__nRows=nRows#Num of rows in the rectangular arrangement
        self.__nColumns=nColumns#Num of cols in the rectangular arrangement
        self.__wordSize=wordSize#in bits, AES is 8 bits word
        if nKeyWords==None:
            self.__nKeyWords=nColumns
        else:
            self.__nKeyWords=nKeyWords#Usually {4,6,8}
        self.debug_stream("Initialising GeneralizedRijndael (%d,%d,%d,%d,%d):"\
                          " block=%dbits key=%dbits"
                          %(self.__nRounds,self.__nRows,self.__nColumns,
                            self.__wordSize,self.__nKeyWords,
                            self.__nColumns*self.__nRows*self.__wordSize,
                            self.__nKeyWords*self.__nRows*self.__wordSize))
        self._keyExpander = KeyExpansion.KeyExpansion(key,
                                                   self.__nRounds,self.__nRows,
                                               self.__nColumns,self.__wordSize,
                                                     self.__nKeyWords,loglevel)

from optparse import OptionParser

def main():
    #---- TODO: introduce parameters to:
    #           - define parameters to use and use random input and key.
    #           - allow to setup by params the input and/or the key, and
    #           - operations to do: cipher and/or decipher
    parser = OptionParser()
    parser.add_option('',"--log-level",default="info",help="Set log level")
    parser.add_option('',"--rounds",default="10",help="Number of rounds")
    parser.add_option('',"--rows",default="4",help="Number of rows")
    parser.add_option('',"--columns",default="4",help="Number of columns")
    parser.add_option('',"--wordsize",default="8",help="bit size of the word")
    parser.add_option('',"--kolumns",default="4",
                                           help="Number of columns of the key")
    (options, args) = parser.parse_args()
    gr = GeneralizedRijndael(key=0,
                             nRounds=int(options.rounds),
                             nRows=int(options.rows),
                             nColumns=int(options.columns),
                             wordSize=int(options.wordsize),
                             nKeyWords=int(options.kolumns),
                             loglevel=Logger.levelFromMeaning(options.log_level))
    #---- TODO: 

if __name__ == "__main__":
    main()
