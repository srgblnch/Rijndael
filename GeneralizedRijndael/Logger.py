#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: Logger.pyx
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

def levelFromMeaning(value):
    try:
        return {'error':Logger.error,
                'warning':Logger.warning,
                'info':Logger.info,
                'debug':Logger.debug,
                'trace':Logger.trace}[value]
    except:
        return Logger.info

#TODO: document the methods
class Logger:
    '''
    '''
    error   = 1
    warning = 2
    info    = 3
    debug   = 4
    trace   = 5
    def __init__(self,loglevel):
        '''
        '''
        self._logLevel = loglevel

    def setLogLevel(self,level):
        self._logLevel = level

    def _areIntegers(self,data):
        '''
        '''
        return type(data) in [int,long]

    def _areLists(self,data):
        '''
        '''
        return type(data)==list

    def _printIntegers(self,data):
        '''
        '''
        return "=%s"%hex(data)

    def _printLists(self,data):
        '''
        '''
        msg = "["
        for element in data:
            if self._areIntegers(element):
                msg+=self._printIntegers(element)#msg+="%4s,"%hex(element)
            elif self._areLists(element):
                self._printLists(element)
                #msg+="["
                #for subelem in element: msg+="%4s,"%hex(subelem)
                #msg=msg[:len(msg)-1]+"],"
            else:
                msg+="%s,"%element
        return msg[:len(msg)-1]+"]"

    def print_line(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        msg=""
        if not round==None: msg+="Round[%d];"%round
        if not operation==None: msg+="%s:"%operation
        msg+=logtext
        if not data==None:
            if self._areIntegers(data):
                msg += self._printIntegers(data)
            elif self._areLists(data):
                msg += self._printLists(data)
            else:
                msg+="=%s"%(data)
        print msg

    def print_stream(self,logtext,loglevel,
                     data=None,round=None,operation=None):
        '''
        '''
        if self._logLevel >= loglevel:
            self.print_line(logtext, data, round, operation)

    def error_stream(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        self.print_stream(logtext,Logger.error,data,round,operation)

    def warning_stream(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        self.print_stream(logtext,Logger.warning,data,round,operation)

    def info_stream(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        self.print_stream(logtext,Logger.info,data,round,operation)

    def debug_stream(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        self.print_stream(logtext,Logger.debug,data,round,operation)

    def trace_stream(self,logtext,data=None,round=None,operation=None):
        '''
        '''
        self.print_stream(logtext,Logger.trace,data,round,operation)