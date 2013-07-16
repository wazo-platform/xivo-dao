# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo.asterisk.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao import line_dao
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehints import CtiPhoneHints
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.extension import Extension as ExtensionSchema
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase

USER_ID = 5
LINE_NUMBER = '1666'


class TestLineFeaturesDAO(DAOTestCase):

    tables = [
        LineFeatures,
        SCCPLine,
        UserSIP,
        UserFeatures,
        CtiProfile,
        CtiPresences,
        CtiPhoneHints,
        CtiPhoneHintsGroup,
        ExtensionSchema
    ]

    def setUp(self):
        self.empty_tables()

    def test_find_line_id_by_user_id(self):
        line = self.add_line(iduserfeatures=USER_ID)

        lines = line_dao.find_line_id_by_user_id(USER_ID)

        self.assertEqual(lines[0], line.id)

    def test_number(self):
        line = self.add_line(number=LINE_NUMBER)

        number = line_dao.number(line.id)

        self.assertEqual(number, LINE_NUMBER)

    def test_get_number_by_user_id_not_found(self):
        self.assertRaises(LookupError, line_dao.get_number_by_user_id, USER_ID)

    def test_get_number_by_user_id_found(self):
        self.add_line(number=LINE_NUMBER,
                      iduserfeatures=USER_ID)
        expected_phone_number = LINE_NUMBER

        phone_number = line_dao.get_number_by_user_id(USER_ID)

        self.assertEquals(phone_number, expected_phone_number)

    def test_is_phone_exten(self):
        self.assertFalse(line_dao.is_phone_exten('12345'))
        self.assertFalse(line_dao.is_phone_exten(None))

        self.add_line(number=LINE_NUMBER)

        self.assertTrue(line_dao.is_phone_exten(LINE_NUMBER))

    def _insert_sccpline(self, sccpline_id):
        sccpline = SCCPLine()
        sccpline.id = sccpline_id
        sccpline.name = '1234'
        sccpline.context = 'test'
        sccpline.cid_name = 'Tester One'
        sccpline.cid_num = '1234'

        self.session.begin()
        self.session.add(sccpline)
        self.session.commit()

        return sccpline

    def test_all_with_protocol(self):
        protocol_id = 1
        firstname = 'Lord'
        lastname = 'Sanderson'

        user = self.add_user(firstname=firstname,
                      lastname=lastname)
        self.add_usersip(id=protocol_id)
        self._insert_sccpline(protocol_id)
        self.add_line(protocol='sip',
                      protocolid=protocol_id,
                      iduserfeatures=user.id)
        line = self.add_line(protocol='sccp',
                             protocolid=protocol_id,
                             iduserfeatures=user.id)

        results = line_dao.all_with_protocol('sccp')
        print results
        result_line_id = results[0][0].id
        result_protocol = results[0][0].protocol
        result_firstname = results[0].firstname
        result_lastname = results[0].lastname

        self.assertEqual(len(results), 1)
        self.assertEqual(result_line_id, line.id)
        self.assertEqual(result_protocol, line.protocol)
        self.assertEqual(result_firstname, firstname)
        self.assertEqual(result_lastname, lastname)

    def test_find_context_by_user_id(self):
        self.add_line(context='falafel',
                      iduserfeatures=USER_ID)

        context = line_dao.find_context_by_user_id(USER_ID)

        self.assertEqual('falafel', context)

    def test_get_interface_from_exten_and_context_sip(self):
        protocol = 'sip'
        name = 'abcdef'
        context = 'foobar'
        self.add_line(context=context,
                      name=name,
                      protocol=protocol,
                      number=LINE_NUMBER)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('SIP/abcdef', interface)

    def test_get_interface_from_exten_and_context_sccp(self):
        protocol = 'SCCP'
        name = '1001'
        context = 'foobar'
        self.add_line(context=context,
                      name=name,
                      protocol=protocol,
                      number=LINE_NUMBER)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('SCCP/1001', interface)

    def test_get_interface_from_exten_and_context_custom(self):
        protocol = 'custom'
        name = 'dahdi/g1/12345'
        context = 'foobar'
        self.add_line(context=context,
                      name=name,
                      protocol=protocol,
                      number=LINE_NUMBER)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('dahdi/g1/12345', interface)

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_exten_and_context, '555', 'fijsifjsif')

    def test_get_extension_from_protocol_interface_no_extension(self):
        self.assertRaises(LookupError, line_dao.get_extension_from_protocol_interface, 'SIP', 'abcdef')

    def test_get_extension_from_protocol_interface_sip(self):
        protocol = 'sip'
        name = 'abcdef'
        context = 'default'

        expected_extension = Extension(number=LINE_NUMBER,
                                       context=context,
                                       is_internal=True)
        self.add_line(context=context,
                      name=name,
                      protocol=protocol,
                      number=LINE_NUMBER)

        extension = line_dao.get_extension_from_protocol_interface(protocol, name)

        self.assertEquals(extension, expected_extension)

    def test_get_extension_from_protocol_interface_sccp(self):
        protocol = 'SCCP'
        name = LINE_NUMBER
        context = 'default'

        expected_extension = Extension(number=LINE_NUMBER,
                                       context=context,
                                       is_internal=True)
        self.add_line(context=context,
                      name=name,
                      protocol=protocol.lower(),
                      number=LINE_NUMBER)

        extension = line_dao.get_extension_from_protocol_interface(protocol, name)

        self.assertEquals(extension, expected_extension)

    def test_get_cid_from_sccp_channel(self):
        channel = 'SCCP/1234-000000001'

        self.assertRaises(LookupError, line_dao._get_cid_for_sccp_channel, channel)

        line = SCCPLine()
        line.name = '1234'
        line.context = 'test'
        line.cid_name = 'Tester One'
        line.cid_num = '1234'

        self.session.begin()
        self.session.add(line)
        self.session.commit()

        result = line_dao._get_cid_for_sccp_channel(channel)
        expected = ('"Tester One" <1234>', 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, line_dao._get_cid_for_sccp_channel, 'SIP/abc-123')

    def test_get_cid_for_sip_channel(self):
        channel = 'SIP/abcd-12445'

        self.assertRaises(LookupError, line_dao._get_cid_for_sip_channel, channel)

        line = UserSIP()
        line.name = 'abcd'
        line.type = 'friend'
        line.callerid = '"Tester One" <1234>'

        self.session.begin()
        self.session.add(line)
        self.session.commit()

        result = line_dao._get_cid_for_sip_channel(channel)
        expected = (line.callerid, 'Tester One', '1234')

        self.assertEqual(result, expected)

        self.assertRaises(ValueError, line_dao._get_cid_for_sip_channel, 'sccp/1300@SEP29287324-1')

    @patch('xivo_dao.line_dao._get_cid_for_sccp_channel')
    @patch('xivo_dao.line_dao._get_cid_for_sip_channel')
    def test_get_cid_for_channel(self, get_sip_cid, get_sccp_cid):
        channel = 'DAHDI/i1/12543656-1235'

        self.assertRaises(ValueError, line_dao.get_cid_for_channel, channel)

        cid = ('"Tester One" <555>', 'Tester One', '555')
        channel = 'SIP/abcde-1234'

        get_sip_cid.return_value = cid
        result = line_dao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)

        cid = ('"Tester One" <1111>', 'Tester Two', '1111')
        channel = 'SCCP/1300-00000000012'

        get_sccp_cid.return_value = cid
        result = line_dao.get_cid_for_channel(channel)

        self.assertEqual(result, cid)

    def test_get_interface_from_user_id(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_user_id, 5)

        line = self.add_line(iduserfeatures=USER_ID)

        interface = line_dao.get_interface_from_user_id(USER_ID)

        expected_iface = line.protocol + '/' + line.name

        self.assertEqual(interface, expected_iface)

    def test_get_interface_from_user_id_custom_line(self):
        protocol = 'custom'
        line = self.add_line(protocol=protocol,
                             iduserfeatures=USER_ID)

        interface = line_dao.get_interface_from_user_id(USER_ID)

        self.assertEqual(interface, line.name)

    def test_create(self):
        line = LineFeatures()
        line.number = '1234'
        line.protocolid = 0
        line.protocol = 'sip'
        line.name = 'name'
        line.context = 'default'
        line.provisioningid = 0

        line_dao.create(line)
        self.assertTrue(line_dao.is_phone_exten('1234'))

    def test_delete(self):
        usersip_id = 2
        self.add_usersip(id=usersip_id)
        line = self.add_line(number=LINE_NUMBER,
                             context='default',
                             protocol='sip',
                             protocolid=usersip_id)
        exten = self.add_extension(exten=LINE_NUMBER,
                                   context='default')

        line_dao.delete(line.id)

        self.assertFalse(line_dao.is_phone_exten(LINE_NUMBER))

        inserted_usersip = self.session.query(UserSIP).filter(UserSIP.id == usersip_id).first()
        self.assertEquals(None, inserted_usersip)
        inserted_extension = self.session.query(ExtensionSchema).filter(ExtensionSchema.id == exten.id).first()
        self.assertEquals(None, inserted_extension)

    def test_get(self):
        line = self.add_line()
        result = line_dao.get(line.id)
        self.assertEquals(line, result)
