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
    This file stores the test vectors provided by the fips-197 for the AES256.
"""

aes256 = {}
aes256['key'] = \
    0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
aes256['input'] = 0x00112233445566778899aabbccddeeff
aes256['output'] = 0x8ea2b7ca516745bfeafc49904b496089

aes256_round = {}
aes256_round[0] = {}
aes256_round[0]['start'] = aes256['input']
aes256_round[0]['k_sch'] = 0x000102030405060708090a0b0c0d0e0f
aes256_round[0]['end'] = 0x00102030405060708090a0b0c0d0e0f0

aes256_round[1] = {}
aes256_round[1]['start'] = aes256_round[0]['end']
aes256_round[1]['s_box'] = 0x63cab7040953d051cd60e0e7ba70e18c
aes256_round[1]['s_row'] = 0x6353e08c0960e104cd70b751bacad0e7
aes256_round[1]['m_col'] = 0x5f72641557f5bc92f7be3b291db9f91a
aes256_round[1]['k_sch'] = 0x101112131415161718191a1b1c1d1e1f
aes256_round[1]['end'] = 0x4f63760643e0aa85efa7213201a4e705

aes256_round[2] = {}
aes256_round[2]['start'] = aes256_round[1]['end']
aes256_round[2]['s_box'] = 0x84fb386f1ae1ac97df5cfd237c49946b
aes256_round[2]['s_row'] = 0x84e1fd6b1a5c946fdf4938977cfbac23
aes256_round[2]['m_col'] = 0xbd2a395d2b6ac438d192443e615da195
aes256_round[2]['k_sch'] = 0xa573c29fa176c498a97fce93a572c09c
aes256_round[2]['end'] = 0x1859fbc28a1c00a078ed8aadc42f6109

aes256_round[3] = {}
aes256_round[3]['start'] = aes256_round[2]['end']
aes256_round[3]['s_box'] = 0xadcb0f257e9c63e0bc557e951c15ef01
aes256_round[3]['s_row'] = 0xad9c7e017e55ef25bc150fe01ccb6395
aes256_round[3]['m_col'] = 0x810dce0cc9db8172b3678c1e88a1b5bd
aes256_round[3]['k_sch'] = 0x1651a8cd0244beda1a5da4c10640bade
aes256_round[3]['end'] = 0x975c66c1cb9f3fa8a93a28df8ee10f63

aes256_round[4] = {}
aes256_round[4]['start'] = aes256_round[3]['end']
aes256_round[4]['s_box'] = 0x884a33781fdb75c2d380349e19f876fb
aes256_round[4]['s_row'] = 0x88db34fb1f807678d3f833c2194a759e
aes256_round[4]['m_col'] = 0xb2822d81abe6fb275faf103a078c0033
aes256_round[4]['k_sch'] = 0xae87dff00ff11b68a68ed5fb03fc1567
aes256_round[4]['end'] = 0x1c05f271a417e04ff921c5c104701554

aes256_round[5] = {}
aes256_round[5]['start'] = aes256_round[4]['end']
aes256_round[5]['s_box'] = 0x9c6b89a349f0e18499fda678f2515920
aes256_round[5]['s_row'] = 0x9cf0a62049fd59a399518984f26be178
aes256_round[5]['m_col'] = 0xaeb65ba974e0f822d73f567bdb64c877
aes256_round[5]['k_sch'] = 0x6de1f1486fa54f9275f8eb5373b8518d
aes256_round[5]['end'] = 0xc357aae11b45b7b0a2c7bd28a8dc99fa

aes256_round[6] = {}
aes256_round[6]['start'] = aes256_round[5]['end']
aes256_round[6]['s_box'] = 0x2e5bacf8af6ea9e73ac67a34c286ee2d
aes256_round[6]['s_row'] = 0x2e6e7a2dafc6eef83a86ace7c25ba934
aes256_round[6]['m_col'] = 0xb951c33c02e9bd29ae25cdb1efa08cc7
aes256_round[6]['k_sch'] = 0xc656827fc9a799176f294cec6cd5598b
aes256_round[6]['end'] = 0x7f074143cb4e243ec10c815d8375d54c

aes256_round[7] = {}
aes256_round[7]['start'] = aes256_round[6]['end']
aes256_round[7]['s_box'] = 0xd2c5831a1f2f36b278fe0c4cec9d0329
aes256_round[7]['s_row'] = 0xd22f0c291ffe031a789d83b2ecc5364c
aes256_round[7]['m_col'] = 0xebb19e1c3ee7c9e87d7535e9ed6b9144
aes256_round[7]['k_sch'] = 0x3de23a75524775e727bf9eb45407cf39
aes256_round[7]['end'] = 0xd653a4696ca0bc0f5acaab5db96c5e7d

aes256_round[8] = {}
aes256_round[8]['start'] = aes256_round[7]['end']
aes256_round[8]['s_box'] = 0xf6ed49f950e06576be74624c565058ff
aes256_round[8]['s_row'] = 0xf6e062ff507458f9be50497656ed654c
aes256_round[8]['m_col'] = 0x5174c8669da98435a8b3e62ca974a5ea
aes256_round[8]['k_sch'] = 0x0bdc905fc27b0948ad5245a4c1871c2f
aes256_round[8]['end'] = 0x5aa858395fd28d7d05e1a38868f3b9c5

aes256_round[9] = {}
aes256_round[9]['start'] = aes256_round[8]['end']
aes256_round[9]['s_box'] = 0xbec26a12cfb55dff6bf80ac4450d56a6
aes256_round[9]['s_row'] = 0xbeb50aa6cff856126b0d6aff45c25dc4
aes256_round[9]['m_col'] = 0x0f77ee31d2ccadc05430a83f4ef96ac3
aes256_round[9]['k_sch'] = 0x45f5a66017b2d387300d4d33640a820a
aes256_round[9]['end'] = 0x4a824851c57e7e47643de50c2af3e8c9

aes256_round[10] = {}
aes256_round[10]['start'] = aes256_round[9]['end']
aes256_round[10]['s_box'] = 0xd61352d1a6f3f3a04327d9fee50d9bdd
aes256_round[10]['s_row'] = 0xd6f3d9dda6279bd1430d52a0e513f3fe
aes256_round[10]['m_col'] = 0xbd86f0ea748fc4f4630f11c1e9331233
aes256_round[10]['k_sch'] = 0x7ccff71cbeb4fe5413e6bbf0d261a7df
aes256_round[10]['end'] = 0xc14907f6ca3b3aa070e9aa313b52b5ec

aes256_round[11] = {}
aes256_round[11]['start'] = aes256_round[10]['end']
aes256_round[11]['s_box'] = 0x783bc54274e280e0511eacc7e200d5ce
aes256_round[11]['s_row'] = 0x78e2acce741ed5425100c5e0e23b80c7
aes256_round[11]['m_col'] = 0xaf8690415d6e1dd387e5fbedd5c89013
aes256_round[11]['k_sch'] = 0xf01afafee7a82979d7a5644ab3afe640
aes256_round[11]['end'] = 0x5f9c6abfbac634aa50409fa766677653

aes256_round[12] = {}
aes256_round[12]['start'] = aes256_round[11]['end']
aes256_round[12]['s_box'] = 0xcfde0208f4b418ac5309db5c338538ed
aes256_round[12]['s_row'] = 0xcfb4dbedf4093808538502ac33de185c
aes256_round[12]['m_col'] = 0x7427fae4d8a695269ce83d315be0392b
aes256_round[12]['k_sch'] = 0x2541fe719bf500258813bbd55a721c0a
aes256_round[12]['end'] = 0x516604954353950314fb86e401922521

aes256_round[13] = {}
aes256_round[13]['start'] = aes256_round[12]['end']
aes256_round[13]['s_box'] = 0xd133f22a1aed2a7bfa0f44697c4f3ffd
aes256_round[13]['s_row'] = 0xd1ed44fd1a0f3f2afa4ff27b7c332a69
aes256_round[13]['m_col'] = 0x2c21a820306f154ab712c75eee0da04f
aes256_round[13]['k_sch'] = 0x4e5a6699a9f24fe07e572baacdf8cdea
aes256_round[13]['end'] = 0x627bceb9999d5aaac945ecf423f56da5

aes256_round[14] = {}
aes256_round[14]['start'] = aes256_round[13]['end']
aes256_round[14]['s_box'] = 0xaa218b56ee5ebeacdd6ecebf26e63c06
aes256_round[14]['s_row'] = 0xaa5ece06ee6e3c56dde68bac2621bebf
aes256_round[14]['k_sch'] = 0x24fc79ccbf0979e9371ac23c6d68de36
aes256_round[14]['end'] = aes256['output']

aes256_round[0]['iinput'] = aes256['output']
aes256_round[0]['ik_sch'] = aes256_round[14]['k_sch']
aes256_round[0]['ik_add'] = aes256_round[14]['s_row']
aes256_round[0]['iend'] = aes256_round[14]['s_row']

aes256_round[1]['istart'] = aes256_round[0]['iend']
aes256_round[1]['is_row'] = aes256_round[14]['s_box']
aes256_round[1]['is_box'] = aes256_round[13]['end']
aes256_round[1]['ik_sch'] = aes256_round[13]['k_sch']
aes256_round[1]['ik_add'] = aes256_round[13]['m_col']
aes256_round[1]['iend'] = aes256_round[13]['s_row']

aes256_round[2]['istart'] = aes256_round[1]['iend']
aes256_round[2]['is_row'] = aes256_round[13]['s_box']
aes256_round[2]['is_box'] = aes256_round[12]['end']
aes256_round[2]['ik_sch'] = aes256_round[12]['k_sch']
aes256_round[2]['ik_add'] = aes256_round[12]['m_col']
aes256_round[2]['iend'] = aes256_round[12]['s_row']

aes256_round[3]['istart'] = aes256_round[2]['iend']
aes256_round[3]['is_row'] = aes256_round[12]['s_box']
aes256_round[3]['is_box'] = aes256_round[11]['end']
aes256_round[3]['ik_sch'] = aes256_round[11]['k_sch']
aes256_round[3]['ik_add'] = aes256_round[11]['m_col']
aes256_round[3]['iend'] = aes256_round[11]['s_row']

aes256_round[4]['istart'] = aes256_round[3]['iend']
aes256_round[4]['is_row'] = aes256_round[11]['s_box']
aes256_round[4]['is_box'] = aes256_round[10]['end']
aes256_round[4]['ik_sch'] = aes256_round[10]['k_sch']
aes256_round[4]['ik_add'] = aes256_round[10]['m_col']
aes256_round[4]['iend'] = aes256_round[10]['s_row']

aes256_round[5]['istart'] = aes256_round[4]['iend']
aes256_round[5]['is_row'] = aes256_round[10]['s_box']
aes256_round[5]['is_box'] = aes256_round[9]['end']
aes256_round[5]['ik_sch'] = aes256_round[9]['k_sch']
aes256_round[5]['ik_add'] = aes256_round[9]['m_col']
aes256_round[5]['iend'] = aes256_round[9]['s_row']

aes256_round[6]['istart'] = aes256_round[5]['iend']
aes256_round[6]['is_row'] = aes256_round[9]['s_box']
aes256_round[6]['is_box'] = aes256_round[8]['end']
aes256_round[6]['ik_sch'] = aes256_round[8]['k_sch']
aes256_round[6]['ik_add'] = aes256_round[8]['m_col']
aes256_round[6]['iend'] = aes256_round[8]['s_row']

aes256_round[7]['istart'] = aes256_round[6]['iend']
aes256_round[7]['is_row'] = aes256_round[8]['s_box']
aes256_round[7]['is_box'] = aes256_round[7]['end']
aes256_round[7]['ik_sch'] = aes256_round[7]['k_sch']
aes256_round[7]['ik_add'] = aes256_round[7]['m_col']
aes256_round[7]['iend'] = aes256_round[7]['s_row']

aes256_round[8]['istart'] = aes256_round[7]['iend']
aes256_round[8]['is_row'] = aes256_round[7]['s_box']
aes256_round[8]['is_box'] = aes256_round[6]['end']
aes256_round[8]['ik_sch'] = aes256_round[6]['k_sch']
aes256_round[8]['ik_add'] = aes256_round[6]['m_col']
aes256_round[8]['iend'] = aes256_round[6]['s_row']

aes256_round[9]['istart'] = aes256_round[8]['iend']
aes256_round[9]['is_row'] = aes256_round[6]['s_box']
aes256_round[9]['is_box'] = aes256_round[5]['end']
aes256_round[9]['ik_sch'] = aes256_round[5]['k_sch']
aes256_round[9]['ik_add'] = aes256_round[5]['m_col']
aes256_round[9]['iend'] = aes256_round[5]['s_row']

aes256_round[10]['istart'] = aes256_round[9]['iend']
aes256_round[10]['is_row'] = aes256_round[5]['s_box']
aes256_round[10]['is_box'] = aes256_round[4]['end']
aes256_round[10]['ik_sch'] = aes256_round[4]['k_sch']
aes256_round[10]['ik_add'] = aes256_round[4]['m_col']
aes256_round[10]['iend'] = aes256_round[4]['s_row']

aes256_round[11]['istart'] = aes256_round[10]['iend']
aes256_round[11]['is_row'] = aes256_round[4]['s_box']
aes256_round[11]['is_box'] = aes256_round[3]['end']
aes256_round[11]['ik_sch'] = aes256_round[3]['k_sch']
aes256_round[11]['ik_add'] = aes256_round[3]['m_col']
aes256_round[11]['iend'] = aes256_round[3]['s_row']

aes256_round[12]['istart'] = aes256_round[11]['iend']
aes256_round[12]['is_row'] = aes256_round[3]['s_box']
aes256_round[12]['is_box'] = aes256_round[2]['end']
aes256_round[12]['ik_sch'] = aes256_round[2]['k_sch']
aes256_round[12]['ik_add'] = aes256_round[2]['m_col']
aes256_round[12]['iend'] = aes256_round[2]['s_row']

aes256_round[13]['istart'] = aes256_round[12]['iend']
aes256_round[13]['is_row'] = aes256_round[2]['s_box']
aes256_round[13]['is_box'] = aes256_round[1]['end']
aes256_round[13]['ik_sch'] = aes256_round[1]['k_sch']
aes256_round[13]['ik_add'] = aes256_round[1]['m_col']
aes256_round[13]['iend'] = aes256_round[1]['s_row']

aes256_round[14]['istart'] = aes256_round[13]['iend']
aes256_round[14]['is_row'] = aes256_round[1]['s_box']
aes256_round[14]['is_box'] = aes256_round[0]['end']
aes256_round[14]['ik_sch'] = aes256_round[0]['k_sch']
aes256_round[14]['ik_add'] = aes256['input']
aes256_round[14]['ioutput'] = aes256['input']
