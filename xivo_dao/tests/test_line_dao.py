# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.tests.test_dao import UNKNOWN_ID, UNKNOWN_UUID, DAOTestCase

from .. import line_dao

EXTEN = '1666'


class TestLineFeaturesDAO(DAOTestCase):
    def setUp(self):
        super().setUp()
        self.context = self.add_context()

    def test_get_interface_from_exten_and_context_sip(self):
        name = 'abcdef'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert 'PJSIP/abcdef' == interface

    def test_get_interface_from_exten_and_context_sccp(self):
        name = '1001'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        sccp = self.add_sccpline()
        line = self.add_line(name=name, endpoint_sccp_id=sccp.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert 'SCCP/1001' == interface

    def test_get_interface_from_exten_and_context_custom(self):
        name = 'custom/g1/12345'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        custom = self.add_usercustom()
        line = self.add_line(name=name, endpoint_custom_id=custom.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interface = line_dao.get_interface_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert 'custom/g1/12345' == interface

    def test_get_interface_from_exten_and_context_multiple_lines(self):
        main_exten = '1234'
        main_name = 'iddqd'
        second_exten = '5555'
        second_name = 'idbehold'
        user = self.add_user()

        extension = self.add_extension(exten=main_exten, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=main_name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        extension = self.add_extension(exten=second_exten, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=second_name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line.id)

        interface = line_dao.get_interface_from_exten_and_context(
            second_exten, self.context.name
        )

        assert 'PJSIP/idbehold' == interface

    def test_get_interface_from_exten_and_context_multiple_lines_same_exten(self):
        user = self.add_user()
        extension = self.add_extension(exten=EXTEN, context=self.context.name)

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)
        main_line_name = line.name

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line.id)

        interface = line_dao.get_interface_from_exten_and_context(
            EXTEN, self.context.name
        )

        expected = f'PJSIP/{main_line_name}'
        assert expected == interface

    def test_get_interface_no_matching_exten(self):
        self.assertRaises(
            LookupError,
            line_dao.get_interface_from_exten_and_context,
            '555',
            'fijsifjsif',
        )

    def test_get_interfaces_from_exten_and_context_sip(self):
        name = 'abcdef'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(name=name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interfaces = line_dao.get_interfaces_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert ['PJSIP/abcdef'] == interfaces

    def test_get_interfaces_from_exten_and_context_sccp(self):
        name = '1001'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        sccp = self.add_sccpline()
        line = self.add_line(name=name, endpoint_sccp_id=sccp.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interfaces = line_dao.get_interfaces_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert ['SCCP/1001'] == interfaces

    def test_get_interfaces_from_exten_and_context_custom(self):
        name = 'custom/g1/12345'
        extension = self.add_extension(exten=EXTEN, context=self.context.name)
        custom = self.add_usercustom()
        line = self.add_line(name=name, endpoint_custom_id=custom.id)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        interfaces = line_dao.get_interfaces_from_exten_and_context(
            EXTEN, self.context.name
        )

        assert ['custom/g1/12345'] == interfaces

    def test_get_interfaces_from_exten_and_context_multiple_lines(self):
        main_exten = '1234'
        main_name = 'iddqd'
        second_exten = '5555'
        second_name = 'idbehold'
        user = self.add_user()

        extension = self.add_extension(exten=main_exten, context=self.context.name)
        sip = self.add_endpoint_sip()
        line1 = self.add_line(name=main_name, endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line1.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line1.id)

        extension2 = self.add_extension(exten=second_exten, context=self.context.name)
        sip2 = self.add_endpoint_sip()
        line2 = self.add_line(name=second_name, endpoint_sip_uuid=sip2.uuid)
        self.add_line_extension(line_id=line2.id, extension_id=extension2.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line2.id)

        interfaces = line_dao.get_interfaces_from_exten_and_context(
            second_exten, self.context.name
        )

        assert ['PJSIP/idbehold'] == interfaces

    def test_get_interfaces_from_exten_and_context_multiple_lines_same_exten(self):
        user = self.add_user()
        extension = self.add_extension(exten=EXTEN, context=self.context.name)

        sip1 = self.add_endpoint_sip()
        line1 = self.add_line(endpoint_sip_uuid=sip1.uuid)
        self.add_line_extension(line_id=line1.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line1.id)

        sip2 = self.add_endpoint_sip()
        line2 = self.add_line(endpoint_sip_uuid=sip2.uuid)
        self.add_line_extension(line_id=line2.id, extension_id=extension.id)
        self.add_user_line(user_id=user.id, main_line=False, line_id=line2.id)

        interfaces = line_dao.get_interfaces_from_exten_and_context(
            EXTEN, self.context.name
        )

        expected = [f'PJSIP/{line1.name}', f'PJSIP/{line2.name}']
        assert expected == interfaces

    def test_get_interfaces_no_matching_exten(self):
        self.assertRaises(
            LookupError,
            line_dao.get_interfaces_from_exten_and_context,
            '555',
            'fijsifjsif',
        )

    def test_get_interface_from_line_id(self):
        line_name = 'sdofiuwoe'
        sip = self.add_endpoint_sip()
        line = self.add_line(name=line_name, endpoint_sip_uuid=sip.uuid)

        interface = line_dao.get_interface_from_line_id(line.id)

        expected = f'PJSIP/{line_name}'
        assert expected == interface

    def test_get_interface_from_line_id_sccp(self):
        line_name = '1056'
        sccp = self.add_sccpline()
        line = self.add_line(name=line_name, endpoint_sccp_id=sccp.id)

        interface = line_dao.get_interface_from_line_id(line.id)

        expected = f'SCCP/{line_name}'
        assert expected == interface

    def test_get_interface_from_line_id_not_found(self):
        self.assertRaises(LookupError, line_dao.get_interface_from_line_id, UNKNOWN_ID)

    def test_get_main_extension_context_from_line_id(self):
        main_exten = '1234'
        extension = self.add_extension(exten=main_exten, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        exten, context = line_dao.get_main_extension_context_from_line_id(line.id)

        assert exten == main_exten
        assert context == self.context.name

    def test_get_main_extension_context_from_line_id_unknown(self):
        result = line_dao.get_main_extension_context_from_line_id(UNKNOWN_ID)

        assert result is None

    def test_get_main_extension_context_from_line_id_without_extension(self):
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = line_dao.get_main_extension_context_from_line_id(line.id)

        assert result is None

    def test_get_main_extension_context_from_line_id_with_multiple_extensions(self):
        main_exten = '1234'
        second_exten = '5555'

        extension = self.add_extension(exten=main_exten, context=self.context.name)
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_line_extension(
            line_id=line.id, extension_id=extension.id, main_extension=True
        )

        extension = self.add_extension(exten=second_exten, context=self.context.name)
        self.add_line_extension(line_id=line.id, extension_id=extension.id)

        exten, context = line_dao.get_main_extension_context_from_line_id(line.id)

        assert exten == main_exten
        assert context == self.context.name

    def test_is_line_owned_by_user(self):
        user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        result = line_dao.is_line_owned_by_user(user.uuid, line.id)

        assert result is True

    def test_is_line_owned_by_user_unknown_user(self):
        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)

        result = line_dao.is_line_owned_by_user(UNKNOWN_UUID, line.id)

        assert result is False

    def test_is_line_owned_by_user_unknown_line(self):
        user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=user.id, main_line=True, line_id=line.id)

        result = line_dao.is_line_owned_by_user(user.uuid, UNKNOWN_ID)

        assert result is False

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

        assert main_result is True
        assert secondary_result is True

    def test_is_line_owned_by_user_with_multiple_users(self):
        main_user = self.add_user()
        secondary_user = self.add_user()

        sip = self.add_endpoint_sip()
        line = self.add_line(endpoint_sip_uuid=sip.uuid)
        self.add_user_line(user_id=main_user.id, main_line=True, line_id=line.id)
        self.add_user_line(user_id=secondary_user.id, main_line=False, line_id=line.id)

        main_result = line_dao.is_line_owned_by_user(main_user.uuid, line.id)
        secondary_result = line_dao.is_line_owned_by_user(secondary_user.uuid, line.id)

        assert main_result is True
        assert secondary_result is True
