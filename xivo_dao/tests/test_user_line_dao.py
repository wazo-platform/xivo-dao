# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from mock import patch

from xivo_dao import user_line_dao
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.tests.test_dao import DAOTestCase

USER_ID = 5
LINE_NUMBER = '1666'


class TestUserLineDAO(DAOTestCase):

    def test_find_line_id_by_user_id(self):
        self.add_user_line_with_exten(exten='445')
        self.add_user_line_with_exten(exten='221')
        user_line = self.add_user_line_with_exten(exten=LINE_NUMBER)

        lines = user_line_dao.find_line_id_by_user_id(user_line.user_id)

        self.assertEqual(lines[0], user_line.line_id)

    def test_get_main_exten_by_line_id_with_no_line(self):
        self.assertRaises(LookupError, user_line_dao.get_main_exten_by_line_id, 22)

    def test_get_main_exten_by_line_id(self):
        self.add_user_line_with_exten(exten='445')
        self.add_user_line_with_exten(exten='221')
        user_line = self.add_user_line_with_exten(exten=LINE_NUMBER)

        number = user_line_dao.get_main_exten_by_line_id(user_line.line_id)

        self.assertEqual(number, LINE_NUMBER)

    def test_get_main_exten_by_user_id_with_no_line(self):
        self.assertRaises(LookupError, user_line_dao.get_main_exten_by_user_id, 1234)

    def test_get_main_exten_by_user_id(self):
        self.add_user_line_with_exten(exten='445')
        self.add_user_line_with_exten(exten='221')
        user_line = self.add_user_line_with_exten(exten=LINE_NUMBER)

        number = user_line_dao.get_main_exten_by_user_id(user_line.user_id)

        self.assertEqual(number, LINE_NUMBER)

    def test_get_line_identity_with_no_line(self):
        self.assertRaises(LookupError, user_line_dao.get_line_identity_by_user_id, 1234)

    def test_get_line_identity(self):
        self.add_user_line_with_exten(exten='445')
        self.add_user_line_with_exten(exten='221')
        expected = 'sip/a1b2c3'
        user_line = self.add_user_line_with_exten(protocol='sip',
                                                  name_line='a1b2c3')

        result = user_line_dao.get_line_identity_by_user_id(user_line.user.id)

        self.assertEqual(result, expected)

    def test_is_phone_exten(self):
        self.add_user_line_with_exten(exten='445')
        self.add_user_line_with_exten(exten='221')
        self.assertFalse(user_line_dao.is_phone_exten('12345'))
        self.assertFalse(user_line_dao.is_phone_exten(None))

        self.add_user_line_with_exten(exten=LINE_NUMBER)

        self.assertTrue(user_line_dao.is_phone_exten(LINE_NUMBER))

    def test_all_with_protocol(self):
        protocol_id = 1
        firstname = 'Lord'
        lastname = 'Sanderson'

        self.add_user_line_with_exten(firstname=firstname,
                                      lastname=lastname,
                                      context='falafel',
                                      protocol='sip',
                                      protocolid=protocol_id,
                                      exten='4500')

        user_line_sccp = self.add_user_line_with_exten(firstname=firstname,
                                                       lastname=lastname,
                                                       context='falafel',
                                                       protocol='sccp',
                                                       protocolid=protocol_id,
                                                       exten='2100')

        self.add_usersip(id=protocol_id)
        self.add_sccpline(id=protocol_id)

        results = user_line_dao.all_with_protocol('sccp')

        result_line, result_protocol, result_user = results[0]

        result_line_id = result_line.id
        result_protocol = result_protocol.protocol

        self.assertEqual(len(results), 1)
        self.assertEqual(result_line_id, user_line_sccp.line_id)
        self.assertEqual(result_protocol, user_line_sccp.line.protocol)
        self.assertEqual(result_user.firstname, firstname)
        self.assertEqual(result_user.lastname, lastname)

    def test_get_cid_from_sccp_channel(self):
        channel = 'SCCP/1234-000000001'

        self.assertRaises(LookupError, user_line_dao._get_cid_for_sccp_channel, channel)

        line = SCCPLine()
        line.name = '1234'
        line.context = 'test'
        line.cid_name = 'Tester One'
        line.cid_num = '1234'

        self.add_me(line)

        result = user_line_dao._get_cid_for_sccp_channel(channel)
        expected = ('"Tester One" <1234>', 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, user_line_dao._get_cid_for_sccp_channel, 'SIP/abc-123')

    def test_get_cid_for_sip_channel(self):
        channel = 'SIP/abcd-12445'

        self.assertRaises(LookupError, user_line_dao._get_cid_for_sip_channel, channel)

        line = UserSIP()
        line.name = 'abcd'
        line.type = 'friend'
        line.callerid = '"Tester One" <1234>'
        line.category = 'user'

        self.add_me(line)

        result = user_line_dao._get_cid_for_sip_channel(channel)
        expected = (line.callerid, 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, user_line_dao._get_cid_for_sip_channel, 'sccp/1300@SEP29287324-1')

    @patch('xivo_dao.user_line_dao._get_cid_for_sccp_channel')
    @patch('xivo_dao.user_line_dao._get_cid_for_sip_channel')
    def test_get_cid_for_channel(self, get_sip_cid, get_sccp_cid):
        channel = 'DAHDI/i1/12543656-1235'

        self.assertRaises(ValueError, user_line_dao.get_cid_for_channel, channel)

        cid = ('"Tester One" <555>', 'Tester One', '555')
        channel = 'SIP/abcde-1234'

        get_sip_cid.return_value = cid
        result = user_line_dao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)

        cid = ('"Tester One" <1111>', 'Tester Two', '1111')
        channel = 'SCCP/1300-00000000012'

        get_sccp_cid.return_value = cid
        result = user_line_dao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)
