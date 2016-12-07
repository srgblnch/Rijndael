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
    This file stores the test vectors provided by the fips-197 for the AES128.
"""

aes128 = {}
aes128['key'] = 0x000102030405060708090a0b0c0d0e0f
aes128['input'] = 0x00112233445566778899aabbccddeeff
aes128['output'] = 0x69c4e0d86a7b0430d8cdb78070b4c55a

aes128_round = {}
aes128_round[0] = {}
aes128_round[0]['start'] = aes128['input']
aes128_round[0]['k_sch'] = 0x000102030405060708090a0b0c0d0e0f
aes128_round[0]['end'] = 0x00102030405060708090a0b0c0d0e0f0

aes128_round[1] = {}
aes128_round[1]['start'] = aes128_round[0]['end']
aes128_round[1]['s_box'] = 0x63cab7040953d051cd60e0e7ba70e18c
aes128_round[1]['s_row'] = 0x6353e08c0960e104cd70b751bacad0e7
aes128_round[1]['m_col'] = 0x5f72641557f5bc92f7be3b291db9f91a
aes128_round[1]['k_sch'] = 0xd6aa74fdd2af72fadaa678f1d6ab76fe
aes128_round[1]['end'] = 0x89d810e8855ace682d1843d8cb128fe4

aes128_round[2] = {}
aes128_round[2]['start'] = aes128_round[1]['end']
aes128_round[2]['s_box'] = 0xa761ca9b97be8b45d8ad1a611fc97369
aes128_round[2]['s_row'] = 0xa7be1a6997ad739bd8c9ca451f618b61
aes128_round[2]['m_col'] = 0xff87968431d86a51645151fa773ad009
aes128_round[2]['k_sch'] = 0xb692cf0b643dbdf1be9bc5006830b3fe
aes128_round[2]['end'] = 0x4915598f55e5d7a0daca94fa1f0a63f7

aes128_round[3] = {}
aes128_round[3]['start'] = aes128_round[2]['end']
aes128_round[3]['s_box'] = 0x3b59cb73fcd90ee05774222dc067fb68
aes128_round[3]['s_row'] = 0x3bd92268fc74fb735767cbe0c0590e2d
aes128_round[3]['m_col'] = 0x4c9c1e66f771f0762c3f868e534df256
aes128_round[3]['k_sch'] = 0xb6ff744ed2c2c9bf6c590cbf0469bf41
aes128_round[3]['end'] = 0xfa636a2825b339c940668a3157244d17

aes128_round[4] = {}
aes128_round[4]['start'] = aes128_round[3]['end']
aes128_round[4]['s_box'] = 0x2dfb02343f6d12dd09337ec75b36e3f0
aes128_round[4]['s_row'] = 0x2d6d7ef03f33e334093602dd5bfb12c7
aes128_round[4]['m_col'] = 0x6385b79ffc538df997be478e7547d691
aes128_round[4]['k_sch'] = 0x47f7f7bc95353e03f96c32bcfd058dfd
aes128_round[4]['end'] = 0x247240236966b3fa6ed2753288425b6c

aes128_round[5] = {}
aes128_round[5]['start'] = aes128_round[4]['end']
aes128_round[5]['s_box'] = 0x36400926f9336d2d9fb59d23c42c3950
aes128_round[5]['s_row'] = 0x36339d50f9b539269f2c092dc4406d23
aes128_round[5]['m_col'] = 0xf4bcd45432e554d075f1d6c51dd03b3c
aes128_round[5]['k_sch'] = 0x3caaa3e8a99f9deb50f3af57adf622aa
aes128_round[5]['end'] = 0xc81677bc9b7ac93b25027992b0261996

aes128_round[6] = {}
aes128_round[6]['start'] = aes128_round[5]['end']
aes128_round[6]['s_box'] = 0xe847f56514dadde23f77b64fe7f7d490
aes128_round[6]['s_row'] = 0xe8dab6901477d4653ff7f5e2e747dd4f
aes128_round[6]['m_col'] = 0x9816ee7400f87f556b2c049c8e5ad036
aes128_round[6]['k_sch'] = 0x5e390f7df7a69296a7553dc10aa31f6b
aes128_round[6]['end'] = 0xc62fe109f75eedc3cc79395d84f9cf5d

aes128_round[7] = {}
aes128_round[7]['start'] = aes128_round[6]['end']
aes128_round[7]['s_box'] = 0xb415f8016858552e4bb6124c5f998a4c
aes128_round[7]['s_row'] = 0xb458124c68b68a014b99f82e5f15554c
aes128_round[7]['m_col'] = 0xc57e1c159a9bd286f05f4be098c63439
aes128_round[7]['k_sch'] = 0x14f9701ae35fe28c440adf4d4ea9c026
aes128_round[7]['end'] = 0xd1876c0f79c4300ab45594add66ff41f

aes128_round[8] = {}
aes128_round[8]['start'] = aes128_round[7]['end']
aes128_round[8]['s_box'] = 0x3e175076b61c04678dfc2295f6a8bfc0
aes128_round[8]['s_row'] = 0x3e1c22c0b6fcbf768da85067f6170495
aes128_round[8]['m_col'] = 0xbaa03de7a1f9b56ed5512cba5f414d23
aes128_round[8]['k_sch'] = 0x47438735a41c65b9e016baf4aebf7ad2
aes128_round[8]['end'] = 0xfde3bad205e5d0d73547964ef1fe37f1

aes128_round[9] = {}
aes128_round[9]['start'] = aes128_round[8]['end']
aes128_round[9]['s_box'] = 0x5411f4b56bd9700e96a0902fa1bb9aa1
aes128_round[9]['s_row'] = 0x54d990a16ba09ab596bbf40ea111702f
aes128_round[9]['m_col'] = 0xe9f74eec023020f61bf2ccf2353c21c7
aes128_round[9]['k_sch'] = 0x549932d1f08557681093ed9cbe2c974e
aes128_round[9]['end'] = 0xbd6e7c3df2b5779e0b61216e8b10b689

aes128_round[10] = {}
aes128_round[10]['start'] = aes128_round[9]['end']
aes128_round[10]['s_box'] = 0x7a9f102789d5f50b2beffd9f3dca4ea7
aes128_round[10]['s_row'] = 0x7ad5fda789ef4e272bca100b3d9ff59f
aes128_round[10]['k_sch'] = 0x13111d7fe3944a17f307a78b4d2b30c5
aes128_round[10]['end'] = aes128['output']

aes128_round[0]['iinput'] = aes128['output']
aes128_round[0]['ik_sch'] = aes128_round[10]['k_sch']
aes128_round[0]['ik_add'] = aes128_round[10]['s_row']
aes128_round[0]['iend'] = aes128_round[10]['s_row']

aes128_round[1]['istart'] = aes128_round[0]['iend']
aes128_round[1]['is_row'] = aes128_round[10]['s_box']
aes128_round[1]['is_box'] = aes128_round[9]['end']
aes128_round[1]['ik_sch'] = aes128_round[9]['k_sch']
aes128_round[1]['ik_add'] = aes128_round[9]['m_col']
aes128_round[1]['iend'] = aes128_round[9]['s_row']

aes128_round[2]['istart'] = aes128_round[1]['iend']
aes128_round[2]['is_row'] = aes128_round[9]['s_box']
aes128_round[2]['is_box'] = aes128_round[8]['end']
aes128_round[2]['ik_sch'] = aes128_round[8]['k_sch']
aes128_round[2]['ik_add'] = aes128_round[8]['m_col']
aes128_round[2]['iend'] = aes128_round[8]['s_row']

aes128_round[3]['istart'] = aes128_round[2]['iend']
aes128_round[3]['is_row'] = aes128_round[8]['s_box']
aes128_round[3]['is_box'] = aes128_round[7]['end']
aes128_round[3]['ik_sch'] = aes128_round[7]['k_sch']
aes128_round[3]['ik_add'] = aes128_round[7]['m_col']
aes128_round[3]['iend'] = aes128_round[7]['s_row']

aes128_round[4]['istart'] = aes128_round[3]['iend']
aes128_round[4]['is_row'] = aes128_round[7]['s_box']
aes128_round[4]['is_box'] = aes128_round[6]['end']
aes128_round[4]['ik_sch'] = aes128_round[6]['k_sch']
aes128_round[4]['ik_add'] = aes128_round[6]['m_col']
aes128_round[4]['iend'] = aes128_round[6]['s_row']

aes128_round[5]['istart'] = aes128_round[4]['iend']
aes128_round[5]['is_row'] = aes128_round[6]['s_box']
aes128_round[5]['is_box'] = aes128_round[5]['end']
aes128_round[5]['ik_sch'] = aes128_round[5]['k_sch']
aes128_round[5]['ik_add'] = aes128_round[5]['m_col']
aes128_round[5]['iend'] = aes128_round[5]['s_row']

aes128_round[6]['istart'] = aes128_round[5]['iend']
aes128_round[6]['is_row'] = aes128_round[5]['s_box']
aes128_round[6]['is_box'] = aes128_round[4]['end']
aes128_round[6]['ik_sch'] = aes128_round[4]['k_sch']
aes128_round[6]['ik_add'] = aes128_round[4]['m_col']
aes128_round[6]['iend'] = aes128_round[4]['s_row']

aes128_round[7]['istart'] = aes128_round[6]['iend']
aes128_round[7]['is_row'] = aes128_round[4]['s_box']
aes128_round[7]['is_box'] = aes128_round[3]['end']
aes128_round[7]['ik_sch'] = aes128_round[3]['k_sch']
aes128_round[7]['ik_add'] = aes128_round[3]['m_col']
aes128_round[7]['iend'] = aes128_round[3]['s_row']

aes128_round[8]['istart'] = aes128_round[7]['iend']
aes128_round[8]['is_row'] = aes128_round[3]['s_box']
aes128_round[8]['is_box'] = aes128_round[2]['end']
aes128_round[8]['ik_sch'] = aes128_round[2]['k_sch']
aes128_round[8]['ik_add'] = aes128_round[2]['m_col']
aes128_round[8]['iend'] = aes128_round[2]['s_row']

aes128_round[9]['istart'] = aes128_round[8]['iend']
aes128_round[9]['is_row'] = aes128_round[2]['s_box']
aes128_round[9]['is_box'] = aes128_round[1]['end']
aes128_round[9]['ik_sch'] = aes128_round[1]['k_sch']
aes128_round[9]['ik_add'] = aes128_round[1]['m_col']
aes128_round[9]['iend'] = aes128_round[1]['s_row']

aes128_round[10]['istart'] = aes128_round[9]['iend']
aes128_round[10]['is_row'] = aes128_round[1]['s_box']
aes128_round[10]['is_box'] = aes128_round[0]['end']
aes128_round[10]['ik_sch'] = aes128['key']
aes128_round[10]['ik_add'] = aes128['input']
aes128_round[10]['ioutput'] = aes128['input']
