# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo.asterisk.extension import Extension
from xivo_dao import line_dao
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.tests.test_dao import DAOTestCase

USER_ID = 5
LINE_NUMBER = '1666'


class TestLineFeaturesDAO(DAOTestCase):

    def _insert_sccpline(self, sccpline_id):
        sccpline = SCCPLine()
        sccpline.id = sccpline_id
        sccpline.name = '1234'
        sccpline.context = 'test'
        sccpline.cid_name = 'Tester One'
        sccpline.cid_num = '1234'

        self.add_me(sccpline)

        return sccpline

    def test_get_peer_name_abcde(self):
        protocol = 'sip'
        name = 'abcde'
        expected_name = '/'.join([protocol, name])

        line = LineFeatures()
        line.device = '1232'
        line.protocolid = 0
        line.context = 'myctx'
        line.number = '1002'
        line.name = name
        line.provisioningid = 123
        line.protocol = protocol

        self.add_me(line)

        peer_name = line_dao.get_peer_name(line.device)

        self.assertEqual(peer_name, expected_name)

    def test_get_peer_name_qwerty(self):
        protocol = 'sip'
        name = 'qwerty'
        expected_name = '/'.join([protocol, name])

        line = LineFeatures()
        line.device = '213'
        line.protocolid = 0
        line.context = 'myctx'
        line.iduserfeatures = 5
        line.number = '1002'
        line.name = name
        line.provisioningid = 123
        line.protocol = protocol

        self.add_me(line)

        peer_name = line_dao.get_peer_name(line.device)

        self.assertEqual(peer_name, expected_name)

    def test_get_peer_name_no_matching_line(self):
        self.assertRaises(LookupError, line_dao.get_peer_name, '222')

    def test_get_interface_from_exten_and_context_sip(self):
        protocol = 'sip'
        name = 'abcdef'
        context = 'foobar'

        self.add_user_line_without_user(exten=LINE_NUMBER, context=context, name=name, protocol=protocol)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('SIP/abcdef', interface)

    def test_get_interface_from_exten_and_context_sccp(self):
        protocol = 'sccp'
        name = '1001'
        context = 'foobar'

        self.add_user_line_without_user(exten=LINE_NUMBER, context=context, name=name, protocol=protocol)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('SCCP/1001', interface)

    def test_get_interface_from_exten_and_context_custom(self):
        protocol = 'custom'
        name = 'dahdi/g1/12345'
        context = 'foobar'

        self.add_user_line_without_user(exten=LINE_NUMBER, context=context, name=name, protocol=protocol)

        interface = line_dao.get_interface_from_exten_and_context(LINE_NUMBER, context)

        self.assertEqual('dahdi/g1/12345', interface)

    def test_get_interface_from_exten_and_context_multiple_lines(self):
        main = dict(exten='1234', context='foobar', name='iddqd', protocol='sip')
        secondary = dict(exten='5555', context='foobar', name='idbehold', protocol='sip')

        user = self.add_user()
        main_line = self.add_user_line_without_user(**main)
        secondary_line = self.add_user_line_without_user(**secondary)
        self.add_user_line(user_id=user.id, main_line=True, line_id=main_line.line_id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=secondary_line.line_id)

        interface = line_dao.get_interface_from_exten_and_context(secondary['exten'], secondary['context'])

        self.assertEqual('SIP/idbehold', interface)

    def test_get_interface_from_exten_and_context_multiple_lines_same_exten(self):
        exten, context = '1002', 'foobar'

        user = self.add_user()
        secondary_line = self.add_line(context=context)
        main_line = self.add_line(context=context)
        extension = self.add_extension(exten=exten, context=context)

        self.add_user_line(line_id=secondary_line.id, user_id=user.id, main_line=False)
        self.add_user_line(line_id=main_line.id, user_id=user.id, main_line=True)
        self.add_line_extension(line_id=secondary_line.id, extension_id=extension.id)
        self.add_line_extension(line_id=main_line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(exten, context)

        expected = '{}/{}'.format(main_line.protocol.upper(), main_line.name)
        self.assertEqual(expected, interface)

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_exten_and_context, '555', 'fijsifjsif')

    def test_get_extension_from_protocol_interface_no_extension(self):
        self.assertRaises(LookupError, line_dao.get_extension_from_protocol_interface, 'SIP', 'abcdef')

    def test_get_extension_from_protocol_interface_sip(self):
        protocol = 'sip'
        name = 'abcdef'
        context = 'default'

        expected_extension = Extension(number=LINE_NUMBER, context=context, is_internal=True)
        self.add_user_line_without_user(exten=LINE_NUMBER, context=context, name=name, protocol=protocol)

        extension = line_dao.get_extension_from_protocol_interface(protocol, name)

        self.assertEqual(extension, expected_extension)

    def test_get_extension_from_protocol_interface_local(self):
        protocol = 'local'
        name = 'id-5@agentcallback'

        self.assertRaises(ValueError,
                          line_dao.get_extension_from_protocol_interface, protocol, name)

    def test_get_extension_from_protocol_interface_sccp(self):
        protocol = 'SCCP'
        name = LINE_NUMBER
        context = 'default'

        expected_extension = Extension(number=LINE_NUMBER, context=context, is_internal=True)
        self.add_user_line_without_user(exten=LINE_NUMBER, context=context, name=name, protocol=protocol.lower())

        extension = line_dao.get_extension_from_protocol_interface(protocol, name)

        self.assertEqual(extension, expected_extension)

    def test_get(self):
        line = self.add_line()
        result = line_dao.get(line.id)
        self.assertEqual(line, result)
