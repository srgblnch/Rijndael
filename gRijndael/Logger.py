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
__copyright__ = "Copyright 2013 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

import bz2
import gzip
from datetime import datetime as _datetime
from threading import Lock as _Lock

global lock
lock = _Lock()


def levelFromMeaning(value):
    try:
        return {'silence': Logger._silence,
                'error': Logger._error,
                'warning': Logger._warning,
                'info': Logger._info,
                'debug': Logger._debug,
                'trace': Logger._trace}[value.lower()]
    except:
        if value is not None:
            print("Not recognised log level '%s', using default 'info' level."
                  % (value))
        return Logger._info


_SILENCE = 0
_ERROR = 1
_WARNING = 2
_INFO = 3
_DEBUG = 4
_TRACE = 5


# TODO: document the methods
class Logger(object):
    '''
    '''
    _silence = _SILENCE
    _error = _ERROR
    _warning = _WARNING
    _info = _INFO
    _debug = _DEBUG
    _trace = _TRACE

    def __init__(self, loglevel=_INFO, file_compression=None):
        '''
        '''
        super(Logger, self).__init__()
        if type(loglevel) == str:
            self._logLevel = levelFromMeaning(loglevel)
        elif type(loglevel) in [int] and _SILENCE < loglevel < _TRACE:
            self._logLevel = loglevel
        elif type(loglevel) is None:
            self._logLevel = _INFO
        else:
            raise EnvironmentError("impossible to setup the log level (%s)"
                                   % (loglevel))
        self._when_build = _datetime.now()
        self._log2file = False
        self._stdout = True
        self._file_suffix = ""
        self._file_extension = "log"
        self._file_compression = None
        self.compressedLogfile = file_compression

    def setLogLevel(self, level):
        self._warning_stream("deprecated call to setLogLevel, use logLevel "
                             "property")
        self._logLevel = level

    @property
    def logLevel(self):
        return self._logLevel

    @property
    def logLevelStr(self):
        return {Logger._silence: 'silence',
                Logger._error: 'error',
                Logger._warning: 'warning',
                Logger._info: 'info',
                Logger._debug: 'debug',
                Logger._trace: 'trace'}[self._logLevel]

    @logLevel.setter
    def logLevel(self, level):
        if type(level) == str:
            self._logLevel = levelFromMeaning(level)
        elif type(level) == int and self._silence <= level <= self._trace:
            self._logLevel = level
        else:
            self._warning_stream("Not understood the logLevel %s" % level)

    @property
    def log2file(self):
        return self._log2file

    @log2file.setter
    def log2file(self, boolean):
        self._log2file = bool(boolean)
        self._debug_stream("Logger to file = %s" % self._log2file)

    @property
    def compressedLogfile(self):
        return self._file_compression is None

    @compressedLogfile.setter
    def compressedLogfile(self, value):
        if value in ['gz']:
            self._file_compression = value
        # TODO :if "value == 'bz2'" append to file doesn't work well

    @property
    def fileSuffix(self):
        return self._file_suffix

    @fileSuffix.setter
    def fileSuffix(self, suffix):
        self._file_suffix = "%s" % (suffix)
        self._debug_stream("New log file name suffix: %s" % self._file_suffix)

    def getLogFileName(self):
        fileName = self._when_build.strftime("%Y%m%d_%H%M%S")
        if self._file_suffix:
            fileName = "%s_%s" % (fileName, self._file_suffix)
        fileName = "%s.%s" % (fileName, self._file_extension)
        if self._file_compression:
            fileName = "%s.%s" % (fileName, self._file_compression)
        return fileName

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, value):
        self._stdout = bool(value)

    def _arePolynomials(self, data):
        '''
        '''
        return str(data.__type__()) == 'Polynomials.BinaryExtensionModulo' or \
            str(data.__type__()) == 'Polynomials.VectorSpaceModulo'

    def _areIntegers(self, data):
        '''
        '''
        return type(data) in [int, long]

    def _areLists(self, data):
        '''
        '''
        return type(data) == list

    def _printIntegers(self, data):
        '''
        '''
        return "%s" % hex(data)

    def _printLists(self, data):
        '''
        '''
        msg = "[ "
        for element in data:
            if self._areIntegers(element):
                msg += "%4s " % (self._printIntegers(element))
            elif self._areLists(element):
                msg += self._printLists(element)
            else:
                msg += "=%s," % (element)
        if msg[len(msg)-1] == ' ':
            msg = msg[:len(msg)-1]
        msg += " ]"
        return msg

    def _printPolynomials(self, data):
        '''
        '''
        return "%s = %s" % ("{0:b}".format(data),
                            self.__interpretToStr__(data))

    def _print_line(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        msg = ""
        if round is not None:
            msg += "Round[%d];" % (round)
        if operation is not None:
            msg += "%s:" % (operation)
        msg += logtext
        if data is not None:
            if self._areIntegers(data):
                msg += "=%s" % (self._printIntegers(data))
            elif self._areLists(data):
                msg += self._printLists(data)
            elif self._arePolynomials(data):
                msg += self._printPolynomials(data)
            else:
                msg += "%s" % (data)
        if self._log2file:
            fileName = self.getLogFileName()
            if self._file_compression == 'bz2':
                with bz2.BZ2File(fileName, 'at', compresslevel=9) as logfile:
                    logfile.write(msg+"\n")
            elif self._file_compression == 'gz':
                with gzip.open(fileName, 'at', compresslevel=9) as logfile:
                    logfile.write(msg+"\n")
            else:
                with open(fileName, 'a') as logfile:
                    logfile.write(msg+"\n")
        if self._stdout:
            print msg

    def _print_stream(self, logtext, loglevel,
                      data=None, round=None, operation=None):
        '''
        '''
        if self._logLevel >= loglevel:
            with lock:
                now = "%s " % (_datetime.now().isoformat())
                self._print_line(now+logtext, data, round, operation)

    def _error_stream(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        self._print_stream("ERROR  :"+logtext, Logger._error, data,
                           round, operation)

    def _warning_stream(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        self._print_stream("WARNING:"+logtext, Logger._warning, data,
                           round, operation)

    def _info_stream(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        self._print_stream("INFO   :"+logtext, Logger._info, data,
                           round, operation)

    def _debug_stream(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        self._print_stream("DEBUG  :"+logtext, Logger._debug, data,
                           round, operation)

    def _trace_stream(self, logtext, data=None, round=None, operation=None):
        '''
        '''
        self._print_stream("TRACE  :"+logtext, Logger._trace, data,
                           round, operation)


def debug(decoratedMethod):
    def magic(self, *args, **kwargs):
        try:
            argout = decoratedMethod(self, *args, **kwargs)
            self._debug_stream("CALL %s(%s, %s): %s"
                               % (decoratedMethod.__name__, args, kwargs,
                                  argout))
        except Exception as e:
            self._error_stream("Exception in %s() exception: %s"
                               % (decoratedMethod.__name__, e))
    return magic


def trace(decoratedMethod):
    def magic(self, *args, **kwargs):
        try:
            self._trace_stream("CALL %s(%s, %s)" % (decoratedMethod.__name__,
                                                    args, kwargs))
            argout = decoratedMethod(self, *args, **kwargs)
            self._trace_stream("RETURN %s: %s" % decoratedMethod.__name__,
                               argout)
            return argout
        except Exception as e:
            self._error_stream("Exception in %s() exception: %s"
                               % (decoratedMethod.__name__, e))
    return magic
