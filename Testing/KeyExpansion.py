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
from optparse import OptionParser
from _FIPS197_AES128 import *
from _FIPS197_AES192 import *
from _FIPS197_AES256 import *


def subkey2int(argin):
    return _Long(4*8).fromArray(argin, 4*4*8)


def int2subkey(argin):
    return _Long(4*8).toArray(argin, 4*4*8)


def hexlist(argin):
    return ["%s" % hex(each) for each in argin]


def test_AES128(loglevel, rounds=10):
    key = aes128['key']
    keyExpansion = KeyExpansion(key, rounds, 4, 4, 8, loglevel=loglevel)
    for round in aes128_round.keys():
        subkey = keyExpansion.getSubKey(round*4, (round+1)*4)
        if len(subkey) > 0:
            if subkey2int(subkey) != aes128_round[round]['k_sch']:
                print("For round %d\n\t%s\n\t%s"
                      % (round, hex(subkey2int(subkey)),
                         hex(aes128_round[round]['k_sch'])))
                print("For round %d\n\t%s\n\t%s"
                      % (round, hexlist(subkey),
                         hexlist(int2subkey(aes128_round[round]['k_sch']))))
                print("error!")
                return False
    return True


def test_AES192(loglevel, rounds=12):
    key = aes192['key']
    keyExpansion = KeyExpansion(key, rounds, 4, 4, 8, nKeyWords=6,
                                loglevel=loglevel)
    for round in aes192_round.keys():
        subkey = keyExpansion.getSubKey(round*4, (round+1)*4)
        if len(subkey) > 0:
            if subkey2int(subkey) != aes192_round[round]['k_sch']:
                print("For round %d\n\t%s\n\t%s"
                      % (round, hex(subkey2int(subkey)),
                         hex(aes192_round[round]['k_sch'])))
                print("For round %d\n\t%s\n\t%s"
                      % (round, hexlist(subkey),
                         hexlist(int2subkey(aes192_round[round]['k_sch']))))
                print("error!")
                return False
    return True


def test_AES256(loglevel, rounds=14):
    key = aes256['key']
    keyExpansion = KeyExpansion(key, rounds, 4, 4, 8, nKeyWords=8,
                                loglevel=loglevel)
    for round in aes256_round.keys():
        subkey = keyExpansion.getSubKey(round*4, (round+1)*4)
        if len(subkey) > 0:
            if subkey2int(subkey) != aes256_round[round]['k_sch']:
                print("For round %d\n\t%s\n\t%s"
                      % (round, hex(subkey2int(subkey)),
                         hex(aes256_round[round]['k_sch'])))
                print("For round %d\n\t%s\n\t%s"
                      % (round, hexlist(subkey),
                         hexlist(int2subkey(aes256_round[round]['k_sch']))))
                print("error!")
                return False
    return True


def main():
    parser = OptionParser()
    parser.add_option('', "--log-level", default="info",
                      help="Set log level: error, warning, info, debug, trace")
    parser.add_option('', "--test", type='str')
    parser.add_option('', "--rounds", type='int', default=0)
    import sys
    (options, args) = parser.parse_args()
    print options
    if options.test.lower() in ["aes128", "aes192", "aes256"]:
        if options.test.lower() == "aes128":
            if options.rounds == 0:
                result = test_AES128(options.log_level)
            else:
                result = test_AES128(options.log_level, rounds=options.rounds)
        elif options.test.lower() == "aes192":
            if options.rounds == 0:
                result = test_AES192(options.log_level)
            else:
                result = test_AES192(options.log_level, rounds=options.rounds)
        elif options.test.lower() == "aes256":
            if options.rounds == 0:
                result = test_AES256(options.log_level)
            else:
                result = test_AES256(options.log_level, rounds=options.rounds)
        else:
            result = False
        if result:
            sys.exit(0)
        sys.exit(-1)
    else:
        for test in [test_AES128,
                     test_AES192,
                     test_AES256]:
            if not test(levelFromMeaning(options.log_level)):
                sys.exit(-1)
        sys.exit(0)

if __name__ == "__main__":
    main()
