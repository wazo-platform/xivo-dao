# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    equal_to,
    is_not,
    none,
    has_length,
    contains,
    has_properties,
    has_property,
    has_items,
    not_,
)


from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import InputError


class TestLineDao(DAOTestCase):

    def add_line(self, **properties):
        properties.setdefault('context', 'default')
        properties.setdefault('provisioningid', 123456)
        line = Line(**properties)
        self.add_me(line)
        return line


class TestFindBy(TestLineDao):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, line_dao.find_by, column=1)

    def test_find_by(self):
        line = self.add_line(provisioningid=234567)
        result = line_dao.find_by(provisioningid=234567)

        assert_that(result.id, equal_to(line.id))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        line_row = self.add_line()
        line = line_dao.find_by(name=line_row.name, tenant_uuids=[tenant.uuid])
        assert_that(line, none())

        line_row = self.add_line(context=context.name)
        line = line_dao.find_by(name=line_row.name, tenant_uuids=[tenant.uuid])
        assert_that(line, equal_to(line_row))


class TestFindAllBy(TestLineDao):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, line_dao.find_by, column=1)

    def test_find_all_by(self):
        line1 = self.add_line(device='deviceid', provisioningid=123456)
        line2 = self.add_line(device='deviceid', provisioningid=234567)
        result = line_dao.find_all_by(device='deviceid')

        assert_that(
            result,
            has_items(
                has_property('id', line1.id),
                has_property('id', line2.id)),
        )

    def test_find_all_by_multi_tenant(self):
        tenant = self.add_tenant()
        context_1 = self.add_context(tenant_uuid=tenant.uuid)
        context_2 = self.add_context()

        line1 = self.add_line(device='device', context=context_1.name)
        line2 = self.add_line(device='device', context=context_2.name)

        tenants = [tenant.uuid, self.default_tenant.uuid]
        lines = line_dao.find_all_by(device='device', tenant_uuids=tenants)
        assert_that(lines, has_items(line1, line2))

        tenants = [tenant.uuid]
        lines = line_dao.find_all_by(device='device', tenant_uuids=tenants)
        assert_that(lines, all_of(has_items(line1), not_(has_items(line2))))


class TestGet(TestLineDao):

    def test_get_no_line(self):
        self.assertRaises(NotFoundError, line_dao.get, 666)

    def test_get_minimal_parameters(self):
        context = self.add_context()
        line_row = self.add_line(context=context.name, registrar='default', provisioningid=123456)

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(
                id=line_row.id,
                context=context.name,
                provisioning_code='123456',
                position=1,
                endpoint=none(),
                endpoint_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar='default',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_get_all_parameters(self):
        context = self.add_context()
        line_row = self.add_line(
            context=context.name,
            registrar='default',
            protocol='sip',
            protocolid=1234,
            provisioningid=123456,
            num=2,
        )

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(
                id=line_row.id,
                context=context.name,
                position=2,
                provisioning_code='123456',
                endpoint='sip',
                endpoint_id=1234,
                registrar='default',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_given_line_has_sip_endpoint_when_getting_then_line_has_caller_id(self):
        usersip_row = self.add_usersip(callerid='"Jôhn Smith" <1000>')
        line_row = self.add_line(protocol='sip', protocolid=usersip_row.id)

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(caller_id_name="Jôhn Smith", caller_id_num="1000")
        )

    def test_given_line_has_sccp_endpoint_when_getting_then_line_has_caller_id(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(protocol='sccp', protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(caller_id_name="Jôhn Smith", caller_id_num="1000")
        )

    def test_given_line_has_custom_endpoint_when_getting_then_line_has_no_caller_id(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(protocol='custom', protocolid=custom_row.id)

        line = line_dao.get(line_row.id)

        assert_that(line, has_properties(caller_id_name=none(), caller_id_num=none()))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()
        context = self.add_context(tenant_uuid=tenant.uuid)

        line_row = self.add_line(context=context.name)
        line = line_dao.get(line_row.id, tenant_uuids=[tenant.uuid])
        assert_that(line, equal_to(line_row))

        line_row = self.add_line()
        self.assertRaises(
            NotFoundError,
            line_dao.get, line_row.id, tenant_uuids=[tenant.uuid],
        )


class TestEdit(TestLineDao):

    def test_edit_all_parameters(self):
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        line.context = 'mycontext'
        line.provisioning_code = '234567'
        line.position = 3
        line.registrar = 'otherregistrar'

        line_dao.edit(line)

        edited_line = self.session.query(Line).get(line_row.id)
        assert_that(
            edited_line,
            has_properties(
                id=line.id,
                context='mycontext',
                provisioning_code='234567',
                provisioningid=234567,
                position=3,
                registrar='otherregistrar',
            )
        )

    def test_edit_null_parameters(self):
        line_row = self.add_line(endpoint='sccp', endpoint_id=1234)

        line = line_dao.get(line_row.id)
        line.endpoint = None
        line.endpoint_id = None

        line_dao.edit(line)

        edited_line = self.session.query(Line).get(line_row.id)
        assert_that(
            edited_line,
            has_properties(
                id=line.id,
                endpoint=none(),
                protocol=none(),
                endpoint_id=none(),
                protocolid=none(),
            )
        )

    def test_given_line_has_no_endpoint_when_setting_caller_id_then_raises_error(self):
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', "Jôhn Smith")
        self.assertRaises(InputError, setattr, line, 'caller_id_num', "1000")

    def test_given_line_has_custom_endpoint_when_setting_caller_id_then_raises_error(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(protocol='custom', protocolid=custom_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', "Jôhn Smith")
        self.assertRaises(InputError, setattr, line, 'caller_id_num', "1000")

    def test_given_line_has_sip_endpoint_when_editing_then_usersip_updated(self):
        usersip_row = self.add_usersip(callerid='"Jôhn Smith" <1000>')
        line_row = self.add_line(protocol='sip', protocolid=usersip_row.id)
        line_id = line_row.id
        self.session.expire(line_row)

        line = line_dao.get(line_id)
        line.caller_id_name = "Rôger Rabbit"
        line.caller_id_num = "2000"

        line_dao.edit(line)

        edited_usersip = self.session.query(UserSIP).get(usersip_row.id)
        assert_that(edited_usersip.callerid, equal_to('"Rôger Rabbit" <2000>'))

    def test_given_line_has_sip_endpoint_when_setting_caller_id_to_null_then_raises_error(self):
        usersip_row = self.add_usersip(callerid='"Jôhn Smith" <1000>')
        line_row = self.add_line(protocol='sip', protocolid=usersip_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', None)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', None)

    def test_given_line_has_sccp_endpoint_when_editing_then_sccpline_updated(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(protocol='sccp', protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)
        line.caller_id_name = "Rôger Rabbit"

        line_dao.edit(line)

        edited_sccpline = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(edited_sccpline.cid_name, equal_to("Rôger Rabbit"))

    def test_given_line_has_sccp_endpoint_when_setting_caller_id_to_null_then_raises_error(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(protocol='sccp', protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', None)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', None)

    def test_given_line_has_sccp_endpoint_when_setting_caller_id_num_then_raises_error(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(protocol='sccp', protocolid=sccpline_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', '2000')

    def test_linefeatures_name_updated_after_sip_endpoint_association(self):
        usersip_row = self.add_usersip()
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        _force_relationship_loading = line.endpoint_sip
        line.associate_endpoint(usersip_row)
        line_dao.edit(line)

        edited_linefeatures = self.session.query(Line).get(line_row.id)
        assert_that(edited_linefeatures.name, equal_to(usersip_row.name))

    def test_linefeatures_name_updated_after_sccp_endpoint_association(self):
        sccpline_row = self.add_sccpline()
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        _force_relationship_loading = line.endpoint_sccp
        line.associate_endpoint(sccpline_row)
        line_dao.edit(line)

        edited_linefeatures = self.session.query(Line).get(line_row.id)
        assert_that(edited_linefeatures.name, equal_to(sccpline_row.name))

    def test_linefeatures_name_updated_after_custom_endpoint_association(self):
        usercustom_row = self.add_usercustom()
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        _force_relationship_loading = line.endpoint_custom
        line.associate_endpoint(usercustom_row)
        line_dao.edit(line)

        edited_linefeatures = self.session.query(Line).get(line_row.id)
        assert_that(edited_linefeatures.name, equal_to(usercustom_row.interface))


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        context = self.add_context()
        line = Line(context=context.name, provisioningid=123456)

        created_line = line_dao.create(line)

        assert_that(
            created_line,
            has_properties(
                id=is_not(none()),
                context=context.name,
                position=1,
                endpoint=none(),
                endpoint_id=none(),
                provisioning_code=has_length(6),
                caller_id_name=none(),
                caller_id_num=none(),
                configregistrar='default',
                registrar='default',
                ipfrom='',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_create_all_parameters(self):
        context = self.add_context()
        line = Line(
            context=context.name,
            endpoint='sip',
            endpoint_id=1234,
            provisioning_code='123456',
            position=2,
            registrar='otherregistrar',
        )

        created_line = line_dao.create(line)

        assert_that(
            created_line,
            has_properties(
                id=is_not(none()),
                context=context.name,
                position=2,
                endpoint='sip',
                protocol='sip',
                endpoint_id=1234,
                protocolid=1234,
                provisioning_code='123456',
                provisioningid=123456,
                caller_id_name=none(),
                caller_id_num=none(),
                registrar='otherregistrar',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_when_setting_caller_id_to_null_then_nothing_happens(self):
        line = Line(context='default', position=1, registrar='default')
        line.caller_id_name = None
        line.caller_id_num = None

    def test_when_creating_with_caller_id_then_raises_error(self):
        self.assertRaises(InputError, Line, caller_id_name="Jôhn Smith")
        self.assertRaises(InputError, Line, caller_id_num="1000")


class TestDelete(DAOTestCase):

    def test_delete(self):
        line_row = self.add_line()

        line_dao.delete(line_row)

        deleted_line = self.session.query(Line).get(line_row.id)
        assert_that(deleted_line, none())

    def test_given_line_has_sip_endpoint_when_deleting_then_sip_endpoint_deleted(self):
        usersip_row = self.add_usersip()
        line_row = self.add_line(protocol='sip', protocolid=usersip_row.id)

        line_dao.delete(line_row)

        deleted_sip = self.session.query(UserSIP).get(usersip_row.id)
        assert_that(deleted_sip, none())

    def test_given_line_has_sccp_endpoint_when_deleting_then_sccp_endpoint_deleted(self):
        sccpline_row = self.add_sccpline()
        line_row = self.add_line(protocol='sccp', protocolid=sccpline_row.id)

        line_dao.delete(line_row)

        deleted_sccp = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(deleted_sccp, none())

    def test_given_line_has_custom_endpoint_when_deleting_then_custom_endpoint_deleted(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(protocol='custom', protocolid=custom_row.id)

        line_dao.delete(line_row)

        deleted_custom = self.session.query(UserCustom).get(custom_row.id)
        assert_that(deleted_custom, none())


class TestSearch(DAOTestCase):

    def test_search(self):
        line1 = self.add_line(context='default', provisioningid=123456)
        self.add_line(context='default', provisioningid=234567)

        search_result = line_dao.search(search='123456')

        assert_that(
            search_result,
            has_properties(
                total=1,
                items=contains(has_properties(id=line1.id)),
            )
        )

    def test_search_returns_sip_line_associated(self):
        usersip = self.add_usersip()
        line = self.add_line(context='default', protocol='sip', protocolid=usersip.id)

        search_result = line_dao.search()
        assert_that(search_result.total, equal_to(1))

        line = search_result.items[0]
        assert_that(line.protocol, equal_to('sip'))
        assert_that(line.protocolid, usersip.id)
        assert_that(line.endpoint_sip.id, equal_to(usersip.id))

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()
        context1 = self.add_context(tenant_uuid=self.default_tenant.uuid)
        context2 = self.add_context(tenant_uuid=tenant.uuid)

        line1 = self.add_line(context=context1.name)
        line2 = self.add_line(context=context2.name)

        tenants = [tenant.uuid, self.default_tenant.uuid]
        result = line_dao.search(tenant_uuids=tenants)
        assert_that(
            result,
            has_properties(
                items=contains_inanyorder(line1, line2),
            )
        )

        tenants = [tenant.uuid]
        result = line_dao.search(tenant_uuids=tenants)
        assert_that(
            result,
            has_properties(
                items=contains_inanyorder(line2),
            )
        )


class TestRelationship(DAOTestCase):

    def test_endpoint_sip_relationship(self):
        sip_row = self.add_usersip()
        line_row = self.add_line()
        line_row.associate_endpoint(sip_row)

        line = line_dao.get(line_row.id)
        assert_that(line, equal_to(line_row))
        assert_that(line.endpoint_sip, equal_to(sip_row))
        assert_that(line.endpoint_sccp, none())
        assert_that(line.endpoint_custom, none())

    def test_endpoint_sccp_relationship(self):
        sccp_row = self.add_sccpline()
        line_row = self.add_line()
        line_row.associate_endpoint(sccp_row)

        line = line_dao.get(line_row.id)
        assert_that(line, equal_to(line_row))
        assert_that(line.endpoint_sip, none())
        assert_that(line.endpoint_sccp, equal_to(sccp_row))
        assert_that(line.endpoint_custom, none())

    def test_endpoint_custom_relationship(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line()
        line_row.associate_endpoint(custom_row)

        line = line_dao.get(line_row.id)
        assert_that(line, equal_to(line_row))
        assert_that(line.endpoint_sip, none())
        assert_that(line.endpoint_sccp, none())
        assert_that(line.endpoint_custom, equal_to(custom_row))

    def test_extensions_relationship(self):
        extension1_row = self.add_extension()
        extension2_row = self.add_extension()
        line_row = self.add_line()
        self.add_line_extension(
            line_id=line_row.id,
            extension_id=extension1_row.id,
            main_extension=False,
        )
        self.add_line_extension(
            line_id=line_row.id,
            extension_id=extension2_row.id,
            main_extension=True,
        )

        line = line_dao.get(line_row.id)
        assert_that(line, equal_to(line_row))
        assert_that(line.extensions, contains(extension2_row, extension1_row))

    def test_users_relationship(self):
        user1_row = self.add_user()
        user2_row = self.add_user()
        line_row = self.add_line()
        self.add_user_line(line_id=line_row.id, user_id=user1_row.id, main_user=False)
        self.add_user_line(line_id=line_row.id, user_id=user2_row.id, main_user=True)

        line = line_dao.get(line_row.id)
        assert_that(line, equal_to(line_row))
        assert_that(line.users, contains(user2_row, user1_row))
