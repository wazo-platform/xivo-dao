#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mock import patch
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao import linefeaturesdao
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.linefeaturesdao import LineFeaturesDAO


class TestLineFeaturesDAO(DAOTestCase):

    user_id = 5
    line_number = '1666'

    tables = [LineFeatures, SCCPLine, UserSIP]

    def setUp(self):
        self.empty_tables()
        self.dao = LineFeaturesDAO()

    def test_find_line_id_by_user_id(self):
        user = UserFeatures()
        user.id = self.user_id
        user.firstname = 'test_line'

        line = self._insert_line()

        lines = self.dao.find_line_id_by_user_id(self.user_id)

        self.assertEqual(lines[0], line.id)

    def test_number(self):
        line = self._insert_line()

        number = self.dao.number(line.id)

        self.assertEqual(number, line.number)

    def test_is_phone_exten(self):
        self.assertFalse(self.dao.is_phone_exten('12345'))
        self.assertFalse(self.dao.is_phone_exten(None))

        self._insert_line()

        self.assertTrue(self.dao.is_phone_exten(self.line_number))

    def _insert_line(self, context='test_context', name='tre321', protocol='sip'):
        line = LineFeatures()
        line.protocolid = 0
        line.protocol = protocol
        line.name = name
        line.context = context
        line.provisioningid = 0
        line.number = self.line_number
        line.iduserfeatures = self.user_id

        self.session.add(line)
        self.session.commit()

        return line

    def test_find_context_by_user_id(self):
        self._insert_line('falafel')

        context = self.dao.find_context_by_user_id(self.user_id)

        self.assertEqual('falafel', context)

    def test_get_interface_from_exten_and_context_sip(self):
        protocol = 'sip'
        name = 'abcdef'
        context = 'foobar'
        self._insert_line(context, name=name, protocol=protocol)

        interface = self.dao.get_interface_from_exten_and_context(self.line_number, context)

        self.assertEqual('SIP/abcdef', interface)

    def test_get_interface_from_exten_and_context_sccp(self):
        protocol = 'sccp'
        name = '1001'
        context = 'foobar'
        self._insert_line(context, name=name, protocol=protocol)

        interface = self.dao.get_interface_from_exten_and_context(self.line_number, context)

        self.assertEqual('SCCP/1001', interface)

    def test_get_interface_from_exten_and_context_custom(self):
        protocol = 'custom'
        name = 'dahdi/g1/12345'
        context = 'foobar'
        self._insert_line(context, name=name, protocol=protocol)

        interface = self.dao.get_interface_from_exten_and_context(self.line_number, context)

        self.assertEqual('dahdi/g1/12345', interface)

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(LookupError, self.dao.get_interface_from_exten_and_context, '555', 'fijsifjsif')

    def test_get_cid_from_sccp_channel(self):
        channel = 'sccp/1234@SEP0023EBC64F92-1'

        self.assertRaises(LookupError, linefeaturesdao._get_cid_for_sccp_channel, channel)

        line = SCCPLine()
        line.name = '1234'
        line.context = 'test'
        line.cid_name = 'Tester One'
        line.cid_num = '1234'

        self.session.add(line)
        self.session.commit()

        result = linefeaturesdao._get_cid_for_sccp_channel(channel)
        expected = ('"Tester One" <1234>', 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, linefeaturesdao._get_cid_for_sccp_channel, 'SIP/abc-123')

    def test_get_cid_for_sip_channel(self):
        channel = 'SIP/abcd-12445'

        self.assertRaises(LookupError, linefeaturesdao._get_cid_for_sip_channel, channel)

        line = UserSIP()
        line.name = 'abcd'
        line.type = 'friend'
        line.callerid = '"Tester One" <1234>'

        self.session.add(line)
        self.session.commit()

        result = linefeaturesdao._get_cid_for_sip_channel(channel)
        expected = (line.callerid, 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, linefeaturesdao._get_cid_for_sip_channel, 'sccp/1300@SEP29287324-1')

    @patch('xivo_dao.linefeaturesdao._get_cid_for_sccp_channel')
    @patch('xivo_dao.linefeaturesdao._get_cid_for_sip_channel')
    def test_get_cid_for_channel(self, get_sip_cid, get_sccp_cid):
        channel = 'DAHDI/i1/12543656-1235'

        self.assertRaises(ValueError, linefeaturesdao.get_cid_for_channel, channel)

        cid = ('"Tester One" <555>', 'Tester One', '555')
        channel = 'SIP/abcde-1234'

        get_sip_cid.return_value = cid
        result = linefeaturesdao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)

        cid = ('"Tester One" <1111>', 'Tester Two', '1111')
        channel = 'sccp/1300@SEP2897423897-12'

        get_sccp_cid.return_value = cid
        result = linefeaturesdao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)

    def test_get_interface_from_user_id(self):
        self.assertRaises(LookupError, linefeaturesdao.get_interface_from_user_id, 5)

        line = self._insert_line()

        user_id = int(line.iduserfeatures)

        interface = linefeaturesdao.get_interface_from_user_id(user_id)

        expected_iface = line.protocol + '/' + line.name

        self.assertEqual(interface, expected_iface)

    def test_get_interface_from_user_id_custom_line(self):
        protocol = 'custom'
        name = 'dahdi/g1/12345'
        context = 'foobar'
        line = self._insert_line(context, name=name, protocol=protocol)

        user_id = int(line.iduserfeatures)

        interface = linefeaturesdao.get_interface_from_user_id(user_id)

        self.assertEqual(interface, name)
