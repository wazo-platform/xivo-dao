# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as call_permission_dao


class TestFind(DAOTestCase):

    def test_find_no_call_permission(self):
        result = call_permission_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        call_permission_row = self.add_call_permission(
            name='Bôb',
            password='âS$%?^ééé',
            mode='allow',
            extensions=['123', '456'],
            enabled=True,
            description='description',
        )

        call_permission = call_permission_dao.find(call_permission_row.id)

        assert_that(call_permission, equal_to(call_permission_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        call_permission = self.add_call_permission(tenant_uuid=tenant.uuid)

        result = call_permission_dao.find(call_permission.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(call_permission))

        result = call_permission_dao.find(call_permission.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_call_permission(self):
        self.assertRaises(NotFoundError, call_permission_dao.get, 42)

    def test_get(self):
        call_permission_row = self.add_call_permission()

        call_permission = call_permission_dao.get(call_permission_row.id)

        assert_that(call_permission.id, equal_to(call_permission.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        call_permission_row = self.add_call_permission(tenant_uuid=tenant.uuid)
        call_permission = call_permission_dao.get(call_permission_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_permission, equal_to(call_permission_row))

        call_permission_row = self.add_call_permission()
        self.assertRaises(
            NotFoundError,
            call_permission_dao.get, call_permission_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_permission_dao.find_by, invalid=42)

    def test_find_by_name(self):
        call_permission_row = self.add_call_permission(name='Jôhn')

        call_permission = call_permission_dao.find_by(name='Jôhn')

        assert_that(call_permission.id, equal_to(call_permission_row.id))
        assert_that(call_permission.name, equal_to('Jôhn'))

    def test_given_call_permission_does_not_exist_then_returns_null(self):
        call_permission = call_permission_dao.find_by(name='42')

        assert_that(call_permission, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        call_permission_row = self.add_call_permission()
        call_permission = call_permission_dao.find_by(id=call_permission_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_permission, none())

        call_permission_row = self.add_call_permission(tenant_uuid=tenant.uuid)
        call_permission = call_permission_dao.find_by(id=call_permission_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_permission, equal_to(call_permission_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_permission_dao.get_by, invalid=42)

    def test_get_by_name(self):
        call_permission_row = self.add_call_permission(name='Jôhn')

        call_permission = call_permission_dao.get_by(name='Jôhn')

        assert_that(call_permission.id, equal_to(call_permission_row.id))
        assert_that(call_permission.name, equal_to('Jôhn'))

    def test_given_call_permission_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, call_permission_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        call_permission_row = self.add_call_permission()
        self.assertRaises(
            NotFoundError,
            call_permission_dao.get_by, id=call_permission_row.id, tenant_uuids=[tenant.uuid],
        )

        call_permission_row = self.add_call_permission(tenant_uuid=tenant.uuid)
        call_permission = call_permission_dao.get_by(id=call_permission_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_permission, equal_to(call_permission_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_call_permissions(self):
        result = call_permission_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        call_permission1 = self.add_call_permission(name='bob', enabled=True)
        call_permission2 = self.add_call_permission(name='alice', enabled=True)

        call_permissions = call_permission_dao.find_all_by(enabled=True)

        assert_that(call_permissions, has_items(
            has_property('id', call_permission1.id),
            has_property('id', call_permission2.id),
        ))

    def test_find_all_by_native_column(self):
        call_permission1 = self.add_call_permission(name='bob', description='description')
        call_permission2 = self.add_call_permission(name='alice', description='description')

        call_permissions = call_permission_dao.find_all_by(description='description')

        assert_that(call_permissions, has_items(
            has_property('id', call_permission1.id),
            has_property('id', call_permission2.id),
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        call_permission1 = self.add_call_permission(description='description', tenant_uuid=tenant.uuid)
        call_permission2 = self.add_call_permission(description='description')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        call_permissions = call_permission_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(call_permissions, has_items(call_permission1, call_permission2))

        tenants = [tenant.uuid]
        call_permissions = call_permission_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(call_permissions, all_of(has_items(call_permission1), not_(has_items(call_permission2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = call_permission_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_call_permissions_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_call_permission_then_returns_one_result(self):
        call_permission = self.add_call_permission(name='bob')
        expected = SearchResult(1, [call_permission])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        call_permission1 = self.add_call_permission(name='sort1')
        call_permission2 = self.add_call_permission(name='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [call_permission1, call_permission2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [call_permission2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleCallPermissions(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.call_permission1 = self.add_call_permission(name='Ashton', description='resto', mode='allow')
        self.call_permission2 = self.add_call_permission(name='Beaugarton', description='bar')
        self.call_permission3 = self.add_call_permission(name='Casa', description='resto')
        self.call_permission4 = self.add_call_permission(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.call_permission2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.call_permission1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.call_permission2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.call_permission1, self.call_permission3, self.call_permission4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.call_permission1])
        self.assert_search_returns_result(expected_allow, mode='allow')

        expected_all_deny = SearchResult(3, [self.call_permission2, self.call_permission3, self.call_permission4])
        self.assert_search_returns_result(expected_all_deny, mode='deny')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.call_permission1,
            self.call_permission2,
            self.call_permission3,
            self.call_permission4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.call_permission4,
            self.call_permission3,
            self.call_permission2,
            self.call_permission1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_permission1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_permission2, self.call_permission3, self.call_permission4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.call_permission2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            skip=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_when_creating_with_invalid_mode_then_raises_error(self):
        self.assertRaises(InputError, CallPermission, mode='invalid_mode')

    def test_create_minimal_fields(self):
        call_permission_model = CallPermission(tenant_uuid=self.default_tenant.uuid, name='Jôhn')
        call_permission = call_permission_dao.create(call_permission_model)

        self.session.expire_all()
        assert_that(inspect(call_permission).persistent)
        assert_that(call_permission, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            name="Jôhn",
            password=none(),
            mode='deny',
            enabled=True,
            description=none(),
            extensions=[],

            passwd='',
            authorization=0,
            commented=0,
            rightcallextens=[],
        ))

    def test_create_with_all_fields(self):
        call_permission_model = CallPermission(
            tenant_uuid=self.default_tenant.uuid,
            name='rîghtcall1',
            password='P$WDéẁ',
            mode='allow',
            enabled=False,
            description='description',
            extensions=['123', '456'],
        )

        call_permission = call_permission_dao.create(call_permission_model)

        self.session.expire_all()
        assert_that(inspect(call_permission).persistent)
        assert_that(call_permission, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            name='rîghtcall1',
            password='P$WDéẁ',
            mode='allow',
            enabled=False,
            description='description',
            extensions=contains_inanyorder('123', '456'),

            passwd='P$WDéẁ',
            authorization=1,
            commented=1,
            rightcallextens=contains_inanyorder(
                has_properties(rightcallid=call_permission.id, exten='123'),
                has_properties(rightcallid=call_permission.id, exten='456'),
            )
        ))

    def test_create_duplicate_extension(self):
        call_permission_model = CallPermission(
            tenant_uuid=self.default_tenant.uuid,
            name='Jôhn',
            extensions=['123', '123'],
        )
        call_permission = call_permission_dao.create(call_permission_model)

        self.session.expire_all()
        assert_that(inspect(call_permission).persistent)
        assert_that(call_permission, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            name="Jôhn",
            password=none(),
            mode='deny',
            enabled=True,
            description=none(),
            extensions=['123'],

            passwd='',
            authorization=0,
            commented=0,
            rightcallextens=contains_inanyorder(
                has_properties(rightcallid=call_permission.id, exten='123'),
            )
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        call_permission = self.add_call_permission(
            name='rîghtcall1',
            password='P$WDéẁ',
            mode='deny',
            enabled=True,
            description='tototo',
            extensions=['123', '456'],
        )

        self.session.expire_all()
        call_permission.name = 'denỳallfriends'
        call_permission.password = 'Alhahlalahl'
        call_permission.mode = 'allow'
        call_permission.enabled = False
        call_permission.description = 'description'
        call_permission.extensions = ['789', '321', '654']

        call_permission_dao.edit(call_permission)

        self.session.expire_all()
        assert_that(call_permission, has_properties(
            name='denỳallfriends',
            passwd='Alhahlalahl',
            authorization=1,
            commented=1,
            description='description',
            rightcallextens=contains_inanyorder(
                has_properties(rightcallid=call_permission.id, exten='789'),
                has_properties(rightcallid=call_permission.id, exten='321'),
                has_properties(rightcallid=call_permission.id, exten='654'),
            )
        ))

    def test_edit_set_fields_to_null(self):
        call_permission = self.add_call_permission(
            name='rîghtcall1',
            password='P$WDéẁ',
            mode='deny',
            enabled=True,
            description='tototo',
            extensions=['123', '456'],
        )

        self.session.expire_all()
        call_permission.password = None
        call_permission.description = None

        call_permission_dao.edit(call_permission)

        self.session.expire_all()
        assert_that(call_permission, has_properties(
            passwd='',
            description=none(),
        ))

    def test_edit_extensions_with_same_value(self):
        call_permission = self.add_call_permission(
            name='rîghtcall1',
            extensions=['123', '456'],
        )

        self.session.expire_all()
        call_permission.extensions = ['789', '123']

        call_permission_dao.edit(call_permission)

        self.session.expire_all()
        assert_that(call_permission, has_properties(
            name='rîghtcall1',
            rightcallextens=contains_inanyorder(
                has_properties(rightcallid=call_permission.id, exten='789'),
                has_properties(rightcallid=call_permission.id, exten='123'),
            )
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        call_permission = self.add_call_permission(name='Delete')

        call_permission_dao.delete(call_permission)

        assert_that(inspect(call_permission).deleted)

    def test_delete_references_to_other_tables(self):
        user = self.add_user()
        group = self.add_group()
        outcall = self.add_outcall()

        call_permission = self.add_call_permission(name='Delete')
        self.add_user_call_permission(rightcallid=call_permission.id, typeval=str(user.id))
        self.add_group_call_permission(rightcallid=call_permission.id, typeval=str(group.id))
        self.add_outcall_call_permission(rightcallid=call_permission.id, typeval=str(outcall.id))

        call_permission_dao.delete(call_permission)

        assert_that(self.session.query(RightCallMember).first(), none())
