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

class GeneralizedRijndael(Logger.Logger):
    def __init__(self,loglevel):
        Logger.Logger.__init__(self,loglevel)
        self.debug_stream("Init GeneralizedRijndael")

from optparse import OptionParser

def main():
    #---- TODO: introduce parameters to:
    #           - define parameters to use and use random input and key.
    #           - allow to setup by params the input and/or the key, and
    #           - operations to do: cipher and/or decipher
    parser = OptionParser()
    parser.add_option('-l',"--log-level",default="info",help="Set log level")
    (options, args) = parser.parse_args()
    gr = GeneralizedRijndael(Logger.log_level(options.log_level))
    #---- TODO: 

if __name__ == "__main__":
    main()
