# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.tests.test_dao import (
    DAOTestCase,
    UNKNOWN_UUID,
    UNKNOWN_ID,
)

from .. import line_dao

EXTEN = '1666'
CONTEXT = 'foobar'


class TestLineFeaturesDAO(DAOTestCase):

    def setUp(self):
        super().setUp()
        self.context = self.add_context(name=CONTEXT)

    def test_get_interface_from_exten_and_context_sip(self):
        name = 'abcdef'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('PJSIP/abcdef', interface)

    def test_get_interface_from_exten_and_context_sccp(self):
        name = '1001'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        sccp = self.add_sccpline()
        line = self.add_line(name=name, endpoint_sccp_id=sccp.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('SCCP/1001', interface)

    def test_get_interface_from_exten_and_context_custom(self):
        name = 'custom/g1/12345'
        extension = self.add_extension(exten=EXTEN, context=CONTEXT)
        custom = self.add_usercustom()
        line = self.add_line(name=name, endpoint_custom_id=custom.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(EXTEN, CONTEXT)

        self.assertEqual('custom/g1/12345', interface)

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

        self.assertEqual('PJSIP/idbehold', interface)

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

        expected = f'PJSIP/{main_line_name}'
        self.assertEqual(expected, interface)

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_exten_and_context, '555', 'fijsifjsif')

    def test_get_interface_from_line_id(self):
        line_name = 'sdofiuwoe'
        sip = self.add_endpoint_sip()
        line = self.add_line(name=line_name, endpoint_sip_uuid=sip.uuid)

        interface = line_dao.get_interface_from_line_id(line.id)

        expected = f'PJSIP/{line_name}'
        self.assertEqual(expected, interface)

    def test_get_interface_from_line_id_sccp(self):
        line_name = '1056'
        sccp = self.add_sccpline()
        line = self.add_line(name=line_name, endpoint_sccp_id=sccp.id)

        interface = line_dao.get_interface_from_line_id(line.id)

        expected = f'SCCP/{line_name}'
        self.assertEqual(expected, interface)

    def test_get_interface_from_line_id_not_found(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_line_id, UNKNOWN_ID)

    def test_get_main_extension_context_from_line_id(self):
        main_exten = '1234'
        extension = self.add_extension(exten=main_exten, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        exten, context = line_dao.get_main_extension_context_from_line_id(line.id)

        self.assertEqual(exten, main_exten)
        self.assertEqual(context, CONTEXT)

    def test_get_main_extension_context_from_line_id_unknown(self):
        result = line_dao.get_main_extension_context_from_line_id(UNKNOWN_ID)

        self.assertEqual(result, None)

    def test_get_main_extension_context_from_line_id_without_extension(self):
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = line_dao.get_main_extension_context_from_line_id(line.id)

        self.assertEqual(result, None)

    def test_get_main_extension_context_from_line_id_with_multiple_extensions(self):
        main_exten = '1234'
        second_exten = '5555'

        extension = self.add_extension(exten=main_exten, context=CONTEXT)
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id, main_extension=True)

        extension = self.add_extension(exten=second_exten, context=CONTEXT)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        exten, context = line_dao.get_main_extension_context_from_line_id(line.id)

        self.assertEqual(exten, main_exten)
        self.assertEqual(context, CONTEXT)

    def test_is_line_owned_by_user(self):
        user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        result = line_dao.is_line_owned_by_user(user.uuid, line.id)

        self.assertEqual(result, True)

    def test_is_line_owned_by_user_unknown_user(self):
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = line_dao.is_line_owned_by_user(UNKNOWN_UUID, line.id)

        self.assertEqual(result, False)

    def test_is_line_owned_by_user_unknown_line(self):
        user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        result = line_dao.is_line_owned_by_user(user.uuid, UNKNOWN_ID)

        self.assertEqual(result, False)

    def test_is_line_owned_by_user_with_multiple_lines(self):
        user = self.add_user()

        sip = self.add_endpoint_sip()
        main_line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=True, line_id=main_line.id)

        sip = self.add_endpoint_sip()
        secondary_line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=False, line_id=secondary_line.id)

        main_result = line_dao.is_line_owned_by_user(user.uuid, main_line.id)
        secondary_result = line_dao.is_line_owned_by_user(user.uuid, secondary_line.id)

        self.assertEqual(main_result, True)
        self.assertEqual(secondary_result, True)

    def test_is_line_owned_by_user_with_multiple_users(self):
        main_user = self.add_user()
        secondary_user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=main_user.id, main_line=True, line_id=line.id)
        self.add_user_line(user_id=secondary_user.id, main_line=False, line_id=line.id)

        main_result = line_dao.is_line_owned_by_user(main_user.uuid, line.id)
        secondary_result = line_dao.is_line_owned_by_user(secondary_user.uuid, line.id)

        self.assertEqual(main_result, True)
        self.assertEqual(secondary_result, True)
