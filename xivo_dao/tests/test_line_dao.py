# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.tests.test_dao import DAOTestCase

from .. import line_dao

EXTEN = '1666'
CONTEXT = 'foobar'


class TestLineFeaturesDAO(DAOTestCase):

    def test_get_interface_from_exten_and_context_sip(self):
        name = 'abcdef'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('SIP/abcdef', interface)

    def test_get_interface_from_exten_and_context_sccp(self):
        name = '1001'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        sccp = self.add_sccpline()
        line = self.add_line(name=name, endpoint_sccp_id=sccp.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('SCCP/1001', interface)

    def test_get_interface_from_exten_and_context_custom(self):
        name = 'dahdi/g1/12345'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        custom = self.add_usercustom()
        line = self.add_line(name=name, endpoint_custom_id=custom.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('dahdi/g1/12345', interface)

    def test_get_interface_from_exten_and_context_multiple_lines(self):
        main_exten = '1234'
        main_name = 'iddqd'
        second_exten = '5555'
        second_name = 'idbehold'
        user = self.add_user()

        extension = self.add_extension(exten=main_exten, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=main_name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        extension = self.add_extension(exten=second_exten, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=second_name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line.id)

        interface = line_dao.get_interface_from_exten_and_context(second_exten, CONTEXT)

        self.assertEqual('SIP/idbehold', interface)

    def test_get_interface_from_exten_and_context_multiple_lines_same_exten(self):
        user = self.add_user()
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)
        main_line_name = line.name

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        expected = 'SIP/{}'.format(main_line_name)
        self.assertEqual(expected, interface)

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_exten_and_context, '555', 'fijsifjsif')
