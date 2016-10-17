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
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

"""
    This file executes a test of the vectors provided by the fips-197.
"""

from FIPS197_AES128 import *
from FIPS197_AES192 import *
from FIPS197_AES256 import *


def main():
    Errors = []
    for testClass in [AES128, AES192, AES256]:
        try:
            test = testClass()
            test.test()
        except Exception as e:
            Errors += e.message
    if len(Errors) > 0:
        print("\n\tTest failed:")
        for error in Errors:
            print("\t\t%s" % error)
        print("\n")
        sys.exit(-1)
    else:
        print("\tAll has passed\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
