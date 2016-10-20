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


from gRijndael import KeyExpansion
from gRijndael.Logger import levelFromMeaning
from gRijndael.ThirdLevel import Long as _Long
from gRijndaelTest import extractParams
from optparse import OptionParser
from _FIPS197_AES128 import *
from _FIPS197_AES192 import *
from _FIPS197_AES256 import *


def subkey2int(argin, nRows=4, nColumns=4, wordSize=8):
    return _Long(nColumns*wordSize).fromArray(argin, nRows*nColumns*wordSize)


def int2subkey(argin, nRows=4, nColumns=4, wordSize=8):
    return _Long(nColumns*wordSize).toArray(argin, nRows*nColumns*wordSize)


def hexlist(argin, nColumns=4, wordSize=8):
    format = "%%%ds" % (2+((nColumns*wordSize)/4))
    return [format % hex(each) for each in argin]


def test_AES128(loglevel, rounds=10):
    return test_AES(loglevel, rounds, aes128, aes128_round, 4)


def test_AES192(loglevel, rounds=12):
    return test_AES(loglevel, rounds, aes192, aes192_round, 6)


def test_AES256(loglevel, rounds=14):
    return test_AES(loglevel, rounds, aes256, aes256_round, 8)


def test_AES(loglevel, rounds, aes, aes_round, Nk):
    key = aes['key']
    keyExpansion = KeyExpansion(key, rounds, 4, 4, 8, nKeyWords=Nk,
                                loglevel=loglevel)
    for round in aes_round.keys():
        subkey = keyExpansion.getSubKey(round*4, (round+1)*4)
        if len(subkey) > 0:
            if subkey2int(subkey) != aes_round[round]['k_sch']:
                print("For round %d\n\t%s\n\t%s"
                      % (round, hex(subkey2int(subkey)),
                         hex(aes_round[round]['k_sch'])))
                print("For round %d\n\t%s\n\t%s"
                      % (round, hexlist(subkey),
                         hexlist(int2subkey(aes_round[round]['k_sch']))))
                print("error!")
                return False
            else:
                print("Round %d ok:\t%s\t%35s" % (round, hexlist(subkey),
                                                  hex(subkey2int(subkey))))
        else:
            return False
    return True


def expandKey(key, rounds, nRows, nColumns, wordSize, nKeyColumns, loglevel):
    print loglevel
    keyExpansion = KeyExpansion(key, rounds, nRows, nColumns, wordSize,
                                nKeyColumns, loglevel=loglevel)
    print keyExpansion
    for round in range(rounds):
        subkey = keyExpansion.getSubKey(round*nRows, (round+1)*nRows)
        subkeyLst = hexlist(subkey, nColumns, wordSize)
        try:  # FIXME!
            subkeyHex = hex(subkey2int(subkey, nRows, nColumns, wordSize))
        except:
            if len(subkeyLst) == 0:
                subkeyHex = ""
            else:
                subkeyHex = "subkey2int exception"
        print("Round %d:\t%s\t%s" % (round, subkeyLst, subkeyHex))
    print("block size: %d, key size: %d bits (%d blocks of %d bits), "
          "expanded to %d bits (%d rounds)"
          % (nRows*nColumns*wordSize, nRows*nKeyColumns*wordSize, nRows,
             nColumns*wordSize, rounds*nRows*nColumns*wordSize, rounds))


def main():
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    parser.add_option('', "--test", type='str')
    parser.add_option('', "--rounds", type='int', default=0)
    parser.add_option('', "--key", type='int', default=0)
    import sys
    (options, args) = parser.parse_args()
    loglevel = levelFromMeaning(options.log_level)
    if options.test:
        if options.test.lower() in ["aes128", "aes192", "aes256"]:
            if options.test.lower() == "aes128":
                if options.rounds == 0:
                    result = test_AES128(loglevel)
                else:
                    result = test_AES128(loglevel, rounds=options.rounds)
            elif options.test.lower() == "aes192":
                if options.rounds == 0:
                    result = test_AES192(loglevel)
                else:
                    result = test_AES192(loglevel, rounds=options.rounds)
            elif options.test.lower() == "aes256":
                if options.rounds == 0:
                    result = test_AES256(loglevel)
                else:
                    result = test_AES256(loglevel, rounds=options.rounds)
            else:
                result = False
            if result:
                sys.exit(0)
            sys.exit(-1)
        else:
            rounds, nRows, nColumns, wordSize, nKeyColumns = \
                extractParams(options.test)
            expandKey(options.key, rounds, nRows, nColumns, wordSize,
                      nKeyColumns, options.log_level)
    else:
        for test in [test_AES128,
                     test_AES192,
                     test_AES256]:
            if not test(levelFromMeaning(options.log_level)):
                sys.exit(-1)
        sys.exit(0)

if __name__ == "__main__":
    main()
