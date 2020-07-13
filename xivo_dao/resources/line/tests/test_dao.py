# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
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
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError, InputError, ResourceError


class TestFindBy(DAOTestCase):

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


class TestFindAllBy(DAOTestCase):

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


class TestGet(DAOTestCase):

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
                endpoint_sip_uuid=none(),
                endpoint_sccp_id=none(),
                endpoint_custom_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar='default',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_get_all_parameters(self):
        context = self.add_context()
        sip = self.add_endpoint_sip()
        line_row = self.add_line(
            context=context.name,
            registrar='default',
            endpoint_sip_uuid=sip.uuid,
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
                endpoint_sip_uuid=sip.uuid,
                endpoint_sccp_id=none(),
                endpoint_custom_id=none(),
                registrar='default',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    def test_given_line_has_sip_endpoint_when_getting_then_line_has_caller_id(self):
        usersip_row = self.add_endpoint_sip(
            endpoint_section_options=[['callerid', '"Jôhn Smith" <1000>']],
        )
        line_row = self.add_line(endpoint_sip_uuid=usersip_row.uuid)

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(caller_id_name="Jôhn Smith", caller_id_num="1000")
        )

    def test_given_line_has_sccp_endpoint_when_getting_then_line_has_caller_id(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(endpoint_sccp_id=sccpline_row.id)

        line = line_dao.get(line_row.id)

        assert_that(
            line,
            has_properties(caller_id_name="Jôhn Smith", caller_id_num="1000")
        )

    def test_given_line_has_custom_endpoint_when_getting_then_line_has_no_caller_id(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(endpoint_custom_id=custom_row.id)

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


class TestEdit(DAOTestCase):

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
        sccp = self.add_sccpline()
        line_row = self.add_line(endpoint_sccp_id=sccp.id)

        line = line_dao.get(line_row.id)
        line.endpoint_sccp_id = None

        line_dao.edit(line)

        edited_line = self.session.query(Line).get(line_row.id)
        assert_that(
            edited_line,
            has_properties(
                id=line.id,
                endpoint_sip_uuid=none(),
                endpoint_sccp_id=none(),
                endpoint_custom_id=none(),
            )
        )

    def test_given_line_has_no_endpoint_when_setting_caller_id_then_raises_error(self):
        line_row = self.add_line()

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', "Jôhn Smith")
        self.assertRaises(InputError, setattr, line, 'caller_id_num', "1000")

    def test_given_line_has_custom_endpoint_when_setting_caller_id_then_raises_error(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(endpoint_custom_id=custom_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', "Jôhn Smith")
        self.assertRaises(InputError, setattr, line, 'caller_id_num', "1000")

    def test_given_line_has_sip_endpoint_when_editing_then_endpoint_updated(self):
        usersip_row = self.add_endpoint_sip(
            endpoint_section_options=[['callerid', '"Jôhn Smith" <1000>']]
        )
        line_row = self.add_line(endpoint_sip_uuid=usersip_row.uuid)
        line_id = line_row.id
        self.session.expire(line_row)

        line = line_dao.get(line_id)
        line.caller_id_name = "Rôger Rabbit"
        line.caller_id_num = "2000"

        line_dao.edit(line)

        edited_endpoint = self.session.query(EndpointSIP).get(usersip_row.uuid)
        assert_that(edited_endpoint.caller_id, equal_to('"Rôger Rabbit" <2000>'))

    def test_given_line_has_sip_endpoint_when_setting_caller_id_to_null_then_raises_error(self):
        usersip_row = self.add_endpoint_sip(
            endpoint_section_options=[['callerid', '"Jôhn Smith" <1000>']]
        )
        line_row = self.add_line(endpoint_sip_uuid=usersip_row.uuid)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', None)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', None)

    def test_given_line_has_sccp_endpoint_when_editing_then_sccpline_updated(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(endpoint_sccp_id=sccpline_row.id)

        line = line_dao.get(line_row.id)
        line.caller_id_name = "Rôger Rabbit"

        line_dao.edit(line)

        edited_sccpline = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(edited_sccpline.cid_name, equal_to("Rôger Rabbit"))

    def test_given_line_has_sccp_endpoint_when_setting_caller_id_to_null_then_raises_error(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(endpoint_sccp_id=sccpline_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_name', None)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', None)

    def test_given_line_has_sccp_endpoint_when_setting_caller_id_num_then_raises_error(self):
        sccpline_row = self.add_sccpline(cid_name="Jôhn Smith", cid_num="1000")
        line_row = self.add_line(endpoint_sccp_id=sccpline_row.id)

        line = line_dao.get(line_row.id)
        self.assertRaises(InputError, setattr, line, 'caller_id_num', '2000')

    def test_linefeatures_name_updated_after_sip_endpoint_association(self):
        usersip_row = self.add_endpoint_sip()
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
                endpoint_sip_uuid=none(),
                endpoint_sccp_id=none(),
                endpoint_custom_id=none(),
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
        endpoint_sip = self.add_endpoint_sip()
        line = Line(
            context=context.name,
            endpoint_sip_uuid=endpoint_sip.uuid,
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
                endpoint_sip_uuid=endpoint_sip.uuid,
                endpoint_sccp_id=none(),
                endpoint_custom_id=none(),
                provisioning_code='123456',
                provisioningid=123456,
                caller_id_name=none(),
                caller_id_num=none(),
                registrar='otherregistrar',
                tenant_uuid=self.default_tenant.uuid,
            )
        )

    # The caller ID should only be set once associated to update the endpoint
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
        endpoint_sip = self.add_endpoint_sip()
        line_row = self.add_line(endpoint_sip_uuid=endpoint_sip.uuid)

        line_dao.delete(line_row)

        deleted_endpoint_sip = self.session.query(EndpointSIP).get(endpoint_sip.uuid)
        assert_that(deleted_endpoint_sip, none())

    def test_given_line_has_sccp_endpoint_when_deleting_then_sccp_endpoint_deleted(self):
        sccpline_row = self.add_sccpline()
        line_row = self.add_line(endpoint_sccp_id=sccpline_row.id)

        line_dao.delete(line_row)

        deleted_sccp = self.session.query(SCCPLine).get(sccpline_row.id)
        assert_that(deleted_sccp, none())

    def test_given_line_has_custom_endpoint_when_deleting_then_custom_endpoint_deleted(self):
        custom_row = self.add_usercustom()
        line_row = self.add_line(endpoint_custom_id=custom_row.id)

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
        usersip = self.add_endpoint_sip()
        line = self.add_line(context='default', endpoint_sip_uuid=usersip.uuid)

        search_result = line_dao.search()
        assert_that(search_result.total, equal_to(1))

        line = search_result.items[0]
        assert_that(line.endpoint_sip_uuid, usersip.uuid)

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
        sip_row = self.add_endpoint_sip()
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


class TestAssociateSchedule(DAOTestCase):

    def test_associate_application(self):
        line = self.add_line()
        application = self.add_application()

        line_dao.associate_application(line, application)

        self.session.expire_all()
        assert_that(line.application, equal_to(application))
        assert_that(application.lines, contains(line))

    def test_associate_already_associated(self):
        line = self.add_line()
        application = self.add_application()
        line_dao.associate_application(line, application)

        line_dao.associate_application(line, application)

        self.session.expire_all()
        assert_that(line.application, equal_to(application))


class TestDissociateSchedule(DAOTestCase):

    def test_dissociate_line_application(self):
        line = self.add_line()
        application = self.add_application()
        line_dao.associate_application(line, application)

        line_dao.dissociate_application(line, application)

        self.session.expire_all()
        assert_that(line.application, equal_to(None))

    def test_dissociate_line_application_not_associated(self):
        line = self.add_line()
        application = self.add_application()

        line_dao.dissociate_application(line, application)

        self.session.expire_all()
        assert_that(line.application, equal_to(None))


class TestAssociateEndpointSIP(DAOTestCase):

    def test_associate_line_endpoint_sip(self):
        line = self.add_line()
        sip = self.add_usersip()

        line_dao.associate_endpoint_sip(line, sip)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sip_id, equal_to(sip.id))
        assert_that(result.endpoint_sip, equal_to(sip))

    def test_associate_already_associated(self):
        line = self.add_line()
        sip = self.add_usersip()
        line_dao.associate_endpoint_sip(line, sip)

        line_dao.associate_endpoint_sip(line, sip)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sip, equal_to(sip))

    def test_associate_line_sccp_endpoint_sip(self):
        sccp = self.add_sccpline()
        line = self.add_line(endpoint_sccp_id=sccp.id)
        sip = self.add_usersip()

        self.assertRaises(ResourceError, line_dao.associate_endpoint_sip, line, sip)


class TestDissociateEndpointSIP(DAOTestCase):

    def test_dissociate_line_endpoint_sip(self):
        line = self.add_line()
        sip = self.add_usersip()
        line_dao.associate_endpoint_sip(line, sip)

        line_dao.dissociate_endpoint_sip(line, sip)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sip_id, none())
        assert_that(result.endpoint_sip, none())

    def test_dissociate_line_endpoint_sip_not_associated(self):
        line = self.add_line()
        sip = self.add_usersip()

        line_dao.dissociate_endpoint_sip(line, sip)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sip, none())


class TestAssociateEndpointSCCP(DAOTestCase):

    def test_associate_line_endpoint_sccp(self):
        line = self.add_line()
        sccp = self.add_sccpline()

        line_dao.associate_endpoint_sccp(line, sccp)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sccp_id, equal_to(sccp.id))
        assert_that(result.endpoint_sccp, equal_to(sccp))

    def test_associate_already_associated(self):
        line = self.add_line()
        sccp = self.add_sccpline()
        line_dao.associate_endpoint_sccp(line, sccp)

        line_dao.associate_endpoint_sccp(line, sccp)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sccp, equal_to(sccp))

    def test_associate_line_sip_endpoint_sccp(self):
        sip = self.add_usersip()
        line = self.add_line(endpoint_sip_id=sip.id)
        sccp = self.add_sccpline()

        self.assertRaises(ResourceError, line_dao.associate_endpoint_sccp, line, sccp)


class TestDissociateEndpointSCCP(DAOTestCase):

    def test_dissociate_line_endpoint_sccp(self):
        line = self.add_line()
        sccp = self.add_sccpline()
        line_dao.associate_endpoint_sccp(line, sccp)

        line_dao.dissociate_endpoint_sccp(line, sccp)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sccp_id, none())
        assert_that(result.endpoint_sccp, none())

    def test_dissociate_line_endpoint_sccp_not_associated(self):
        line = self.add_line()
        sccp = self.add_sccpline()

        line_dao.dissociate_endpoint_sccp(line, sccp)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_sccp, none())


class TestAssociateEndpointCustom(DAOTestCase):

    def test_associate_line_endpoint_custom(self):
        line = self.add_line()
        custom = self.add_usercustom()

        line_dao.associate_endpoint_custom(line, custom)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_custom_id, equal_to(custom.id))
        assert_that(result.endpoint_custom, equal_to(custom))

    def test_associate_already_associated(self):
        line = self.add_line()
        custom = self.add_usercustom()
        line_dao.associate_endpoint_custom(line, custom)

        line_dao.associate_endpoint_custom(line, custom)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_custom, equal_to(custom))

    def test_associate_line_sip_endpoint_custom(self):
        sip = self.add_usersip()
        line = self.add_line(endpoint_sip_id=sip.id)
        custom = self.add_usercustom()

        self.assertRaises(ResourceError, line_dao.associate_endpoint_custom, line, custom)


class TestDissociateEndpointCustom(DAOTestCase):

    def test_dissociate_line_endpoint_custom(self):
        line = self.add_line()
        custom = self.add_usercustom()
        line_dao.associate_endpoint_custom(line, custom)

        line_dao.dissociate_endpoint_custom(line, custom)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_custom_id, none())
        assert_that(result.endpoint_custom, none())

    def test_dissociate_line_endpoint_custom_not_associated(self):
        line = self.add_line()
        custom = self.add_usercustom()

        line_dao.dissociate_endpoint_custom(line, custom)

        result = self.session.query(Line).first()
        assert_that(result, equal_to(line))
        assert_that(result.endpoint_custom, none())
