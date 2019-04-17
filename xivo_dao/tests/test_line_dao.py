# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.tests.test_dao import DAOTestCase

from .. import line_dao

LINE_NUMBER = '1666'


class TestLineFeaturesDAO(DAOTestCase):

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
