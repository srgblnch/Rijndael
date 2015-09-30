#!/usr/bin/env python

#---- licence header
##############################################################################
##
## file: setup.py
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

_MAJOR_VERSION=0
_MINOR_VERSION=2
_BUILD_VERSION=1
_REVISION_VERSION=1

def VERSION():
    return (_MAJOR_VERSION,_MINOR_VERSION,
            _BUILD_VERSION,_REVISION_VERSION)

def version():
    return '%d.%d.%d-%d'%(_MAJOR_VERSION,_MINOR_VERSION,
                          _BUILD_VERSION,_REVISION_VERSION)
