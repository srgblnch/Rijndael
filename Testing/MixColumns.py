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

from GeneralizedRijndael import MixColumns
from GeneralizedRijndael.Logger import levelFromMeaning
from optparse import OptionParser

def test_standard(loglevel):
    stateMatrix = [[0x00, 0x01, 0x02, 0x03],
                   [0x10, 0x11, 0x12, 0x13],
                   [0x20, 0x21, 0x22, 0x23],
                   [0x30, 0x31, 0x32, 0x33]]
    mixcolumns = MixColumns(4, 4, 8)
    mixcolumns.logLevel = levelFromMeaning(loglevel)
    print("Testing %s, details:\nEach value in a cell will be interpreted "
          "as a polynomial representation of a binary field extension "
          "modulo %s, and the columns as polynomial in a ring modulo %s."
          % (mixcolumns, mixcolumns.SubfieldModulo, 
             mixcolumns.PolynomialRingModulo))
    stateConverted = mixcolumns.do(stateMatrix)
    if mixcolumns.invert(stateConverted) == stateMatrix:
        return True
    print("ALERT:\n\t%s\n!=\n\t%s" % (stateMatrix, stateConverted))
    return False

def main():
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    (options, args) = parser.parse_args()
    import sys
    if test_standard(options.log_level):
        sys.exit(0)
    sys.exit(-1)

if __name__ == "__main__":
    main()
