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
    This file stores the test vectors provided by the fips-197 for the AES192.
"""

aes192 = {}
aes192['key'] = 0x000102030405060708090a0b0c0d0e0f1011121314151617
aes192['input'] = 0x00112233445566778899aabbccddeeff
aes192['output'] = 0xdda97ca4864cdfe06eaf70a0ec0d7191

aes192_round = {}
aes192_round[0] = {}
aes192_round[0]['start'] = aes192['input']
aes192_round[0]['k_sch'] = 0x000102030405060708090a0b0c0d0e0f
aes192_round[0]['end'] = 0x00102030405060708090a0b0c0d0e0f0

aes192_round[1] = {}
aes192_round[1]['start'] = aes192_round[0]['end']
aes192_round[1]['s_box'] = 0x63cab7040953d051cd60e0e7ba70e18c
aes192_round[1]['s_row'] = 0x6353e08c0960e104cd70b751bacad0e7
aes192_round[1]['m_col'] = 0x5f72641557f5bc92f7be3b291db9f91a
aes192_round[1]['k_sch'] = 0x10111213141516175846f2f95c43f4fe
aes192_round[1]['end'] = 0x4f63760643e0aa85aff8c9d041fa0de4

aes192_round[2] = {}
aes192_round[2]['start'] = aes192_round[1]['end']
aes192_round[2]['s_box'] = 0x84fb386f1ae1ac977941dd70832dd769
aes192_round[2]['s_row'] = 0x84e1dd691a41d76f792d389783fbac70
aes192_round[2]['m_col'] = 0x9f487f794f955f662afc86abd7f1ab29
aes192_round[2]['k_sch'] = 0x544afef55847f0fa4856e2e95c43f4fe
aes192_round[2]['end'] = 0xcb02818c17d2af9c62aa64428bb25fd7

aes192_round[3] = {}
aes192_round[3]['start'] = aes192_round[2]['end']
aes192_round[3]['s_box'] = 0x1f770c64f0b579deaaac432c3d37cf0e
aes192_round[3]['s_row'] = 0x1fb5430ef0accf64aa370cde3d77792c
aes192_round[3]['m_col'] = 0xb7a53ecbbf9d75a0c40efc79b674cc11
aes192_round[3]['k_sch'] = 0x40f949b31cbabd4d48f043b810b7b342
aes192_round[3]['end'] = 0xf75c7778a327c8ed8cfebfc1a6c37f53

aes192_round[4] = {}
aes192_round[4]['start'] = aes192_round[3]['end']
aes192_round[4]['s_box'] = 0x684af5bc0acce85564bb0878242ed2ed
aes192_round[4]['s_row'] = 0x68cc08ed0abbd2bc642ef555244ae878
aes192_round[4]['m_col'] = 0x7a1e98bdacb6d1141a6944dd06eb2d3e
aes192_round[4]['k_sch'] = 0x58e151ab04a2a5557effb5416245080c
aes192_round[4]['end'] = 0x22ffc916a81474416496f19c64ae2532

aes192_round[5] = {}
aes192_round[5]['start'] = aes192_round[4]['end']
aes192_round[5]['s_box'] = 0x9316dd47c2fa92834390a1de43e43f23
aes192_round[5]['s_row'] = 0x93faa123c2903f4743e4dd83431692de
aes192_round[5]['m_col'] = 0xaaa755b34cffe57cef6f98e1f01c13e6
aes192_round[5]['k_sch'] = 0x2ab54bb43a02f8f662e3a95d66410c08
aes192_round[5]['end'] = 0x80121e0776fd1d8a8d8c31bc965d1fee

aes192_round[6] = {}
aes192_round[6]['start'] = aes192_round[5]['end']
aes192_round[6]['s_box'] = 0xcdc972c53854a47e5d64c765904cc028
aes192_round[6]['s_row'] = 0xcd54c7283864c0c55d4c727e90c9a465
aes192_round[6]['m_col'] = 0x921f748fd96e937d622d7725ba8ba50c
aes192_round[6]['k_sch'] = 0xf501857297448d7ebdf1c6ca87f33e3c
aes192_round[6]['end'] = 0x671ef1fd4e2a1e03dfdcb1ef3d789b30

aes192_round[7] = {}
aes192_round[7]['start'] = aes192_round[6]['end']
aes192_round[7]['s_box'] = 0x8572a1542fe5727b9e86c8df27bc1404
aes192_round[7]['s_row'] = 0x85e5c8042f8614549ebca17b277272df
aes192_round[7]['m_col'] = 0xe913e7b18f507d4b227ef652758acbcc
aes192_round[7]['k_sch'] = 0xe510976183519b6934157c9ea351f1e0
aes192_round[7]['end'] = 0x0c0370d00c01e622166b8accd6db3a2c

aes192_round[8] = {}
aes192_round[8]['start'] = aes192_round[7]['end']
aes192_round[8]['s_box'] = 0xfe7b5170fe7c8e93477f7e4bf6b98071
aes192_round[8]['s_row'] = 0xfe7c7e71fe7f807047b95193f67b8e4b
aes192_round[8]['m_col'] = 0x6cf5edf996eb0a069c4ef21cbfc25762
aes192_round[8]['k_sch'] = 0x1ea0372a995309167c439e77ff12051e
aes192_round[8]['end'] = 0x7255dad30fb80310e00d6c6b40d0527c

aes192_round[9] = {}
aes192_round[9]['start'] = aes192_round[8]['end']
aes192_round[9]['s_box'] = 0x40fc5766766c7bcae1d7507f09700010
aes192_round[9]['s_row'] = 0x406c501076d70066e17057ca09fc7b7f
aes192_round[9]['m_col'] = 0x7478bcdce8a50b81d4327a9009188262
aes192_round[9]['k_sch'] = 0xdd7e0e887e2fff68608fc842f9dcc154
aes192_round[9]['end'] = 0xa906b254968af4e9b4bdb2d2f0c44336

aes192_round[10] = {}
aes192_round[10]['start'] = aes192_round[9]['end']
aes192_round[10]['s_box'] = 0xd36f3720907ebf1e8d7a37b58c1c1a05
aes192_round[10]['s_row'] = 0xd37e3705907a1a208d1c371e8c6fbfb5
aes192_round[10]['m_col'] = 0x0d73cc2d8f6abe8b0cf2dd9bb83d422e
aes192_round[10]['k_sch'] = 0x859f5f237a8d5a3dc0c02952beefd63a
aes192_round[10]['end'] = 0x88ec930ef5e7e4b6cc32f4c906d29414

aes192_round[11] = {}
aes192_round[11]['start'] = aes192_round[10]['end']
aes192_round[11]['s_box'] = 0xc4cedcabe694694e4b23bfdd6fb522fa
aes192_round[11]['s_row'] = 0xc494bffae62322ab4bb5dc4e6fce69dd
aes192_round[11]['m_col'] = 0x71d720933b6d677dc00b8f28238e0fb7
aes192_round[11]['k_sch'] = 0xde601e7827bcdf2ca223800fd8aeda32
aes192_round[11]['end'] = 0xafb73eeb1cd1b85162280f27fb20d585

aes192_round[12] = {}
aes192_round[12]['start'] = aes192_round[11]['end']
aes192_round[12]['s_box'] = 0x79a9b2e99c3e6cd1aa3476cc0fb70397
aes192_round[12]['s_row'] = 0x793e76979c3403e9aab7b2d10fa96ccc
aes192_round[12]['k_sch'] = 0xa4970a331a78dc09c418c271e3a41d5d
aes192_round[12]['end'] = aes192['output']

aes192_round[0]['iinput'] = aes192['output']
aes192_round[0]['ik_sch'] = aes192_round[12]['k_sch']
aes192_round[0]['ik_add'] = aes192_round[12]['s_row']
aes192_round[0]['iend'] = aes192_round[12]['s_row']

aes192_round[1]['istart'] = aes192_round[0]['iend']
aes192_round[1]['is_row'] = aes192_round[12]['s_box']
aes192_round[1]['is_box'] = aes192_round[11]['end']
aes192_round[1]['ik_sch'] = aes192_round[11]['k_sch']
aes192_round[1]['ik_add'] = aes192_round[11]['m_col']
aes192_round[1]['iend'] = aes192_round[11]['s_row']

aes192_round[2]['istart'] = aes192_round[1]['iend']
aes192_round[2]['is_row'] = aes192_round[11]['s_box']
aes192_round[2]['is_box'] = aes192_round[10]['end']
aes192_round[2]['ik_sch'] = aes192_round[10]['k_sch']
aes192_round[2]['ik_add'] = aes192_round[10]['m_col']
aes192_round[2]['iend'] = aes192_round[10]['s_row']

aes192_round[3]['istart'] = aes192_round[2]['iend']
aes192_round[3]['is_row'] = aes192_round[10]['s_box']
aes192_round[3]['is_box'] = aes192_round[9]['end']
aes192_round[3]['ik_sch'] = aes192_round[9]['k_sch']
aes192_round[3]['ik_add'] = aes192_round[9]['m_col']
aes192_round[3]['iend'] = aes192_round[9]['s_row']

aes192_round[4]['istart'] = aes192_round[3]['iend']
aes192_round[4]['is_row'] = aes192_round[9]['s_box']
aes192_round[4]['is_box'] = aes192_round[8]['end']
aes192_round[4]['ik_sch'] = aes192_round[8]['k_sch']
aes192_round[4]['ik_add'] = aes192_round[8]['m_col']
aes192_round[4]['iend'] = aes192_round[8]['s_row']

aes192_round[5]['istart'] = aes192_round[4]['iend']
aes192_round[5]['is_row'] = aes192_round[8]['s_box']
aes192_round[5]['is_box'] = aes192_round[7]['end']
aes192_round[5]['ik_sch'] = aes192_round[7]['k_sch']
aes192_round[5]['ik_add'] = aes192_round[7]['m_col']
aes192_round[5]['iend'] = aes192_round[7]['s_row']

aes192_round[6]['istart'] = aes192_round[5]['iend']
aes192_round[6]['is_row'] = aes192_round[7]['s_box']
aes192_round[6]['is_box'] = aes192_round[6]['end']
aes192_round[6]['ik_sch'] = aes192_round[6]['k_sch']
aes192_round[6]['ik_add'] = aes192_round[6]['m_col']
aes192_round[6]['iend'] = aes192_round[6]['s_row']

aes192_round[7]['istart'] = aes192_round[6]['iend']
aes192_round[7]['is_row'] = aes192_round[6]['s_box']
aes192_round[7]['is_box'] = aes192_round[5]['end']
aes192_round[7]['ik_sch'] = aes192_round[5]['k_sch']
aes192_round[7]['ik_add'] = aes192_round[5]['m_col']
aes192_round[7]['iend'] = aes192_round[5]['s_row']

aes192_round[8]['istart'] = aes192_round[7]['iend']
aes192_round[8]['is_row'] = aes192_round[5]['s_box']
aes192_round[8]['is_box'] = aes192_round[4]['end']
aes192_round[8]['ik_sch'] = aes192_round[4]['k_sch']
aes192_round[8]['ik_add'] = aes192_round[4]['m_col']
aes192_round[8]['iend'] = aes192_round[4]['s_row']

aes192_round[9]['istart'] = aes192_round[8]['iend']
aes192_round[9]['is_row'] = aes192_round[4]['s_box']
aes192_round[9]['is_box'] = aes192_round[3]['end']
aes192_round[9]['ik_sch'] = aes192_round[3]['k_sch']
aes192_round[9]['ik_add'] = aes192_round[3]['m_col']
aes192_round[9]['iend'] = aes192_round[3]['s_row']

aes192_round[10]['istart'] = aes192_round[9]['iend']
aes192_round[10]['is_row'] = aes192_round[3]['s_box']
aes192_round[10]['is_box'] = aes192_round[2]['end']
aes192_round[10]['ik_sch'] = aes192_round[2]['k_sch']
aes192_round[10]['ik_add'] = aes192_round[2]['m_col']
aes192_round[10]['iend'] = aes192_round[2]['s_row']

aes192_round[11]['istart'] = aes192_round[10]['iend']
aes192_round[11]['is_row'] = aes192_round[2]['s_box']
aes192_round[11]['is_box'] = aes192_round[1]['end']
aes192_round[11]['ik_sch'] = aes192_round[1]['k_sch']
aes192_round[11]['ik_add'] = aes192_round[1]['m_col']
aes192_round[11]['iend'] = aes192_round[1]['s_row']

aes192_round[12]['istart'] = aes192_round[11]['iend']
aes192_round[12]['is_row'] = aes192_round[1]['s_box']
aes192_round[12]['is_box'] = aes192_round[0]['end']
aes192_round[12]['ik_sch'] = aes192_round[0]['k_sch']
aes192_round[12]['ik_add'] = aes192['input']
aes192_round[12]['ioutput'] = aes192['input']
