# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    equal_to,
    empty,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
)

from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.alchemy.pickupmember import PickupMember as CallPickupMember
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as call_pickup_dao


class TestFind(DAOTestCase):

    def test_find_no_call_pickup(self):
        result = call_pickup_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        call_pickup = self.add_pickup()

        result = call_pickup_dao.find(call_pickup.id)

        assert_that(result, equal_to(call_pickup))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        call_pickup = self.add_pickup(tenant_uuid=tenant.uuid)

        result = call_pickup_dao.find(call_pickup.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(call_pickup))

        result = call_pickup_dao.find(call_pickup.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_call_pickup(self):
        self.assertRaises(NotFoundError, call_pickup_dao.get, 42)

    def test_get(self):
        call_pickup = self.add_pickup()

        result = call_pickup_dao.get(call_pickup.id)

        assert_that(result, equal_to(call_pickup))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        call_pickup_row = self.add_pickup(tenant_uuid=tenant.uuid)
        call_pickup = call_pickup_dao.get(call_pickup_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_pickup, equal_to(call_pickup_row))

        call_pickup_row = self.add_pickup()
        self.assertRaises(
            NotFoundError,
            call_pickup_dao.get, call_pickup_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_pickup_dao.find_by, invalid=42)

    def test_find_by_name(self):
        call_pickup_row = self.add_pickup(name='Jôhn')

        call_pickup = call_pickup_dao.find_by(name='Jôhn')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.name, equal_to('Jôhn'))

    def test_find_by_description(self):
        call_pickup_row = self.add_pickup(description='found')

        call_pickup = call_pickup_dao.find_by(description='found')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.description, equal_to('found'))

    def test_find_by_enabled(self):
        call_pickup_row = self.add_pickup(enabled=False)

        call_pickup = call_pickup_dao.find_by(enabled=False)

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.enabled, equal_to(False))

    def test_given_call_pickup_does_not_exist_then_returns_null(self):
        call_pickup = call_pickup_dao.find_by(name='42')

        assert_that(call_pickup, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        call_pickup_row = self.add_pickup()
        call_pickup = call_pickup_dao.find_by(id=call_pickup_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_pickup, none())

        call_pickup_row = self.add_pickup(tenant_uuid=tenant.uuid)
        call_pickup = call_pickup_dao.find_by(id=call_pickup_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_pickup, equal_to(call_pickup_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_pickup_dao.get_by, invalid=42)

    def test_get_by_name(self):
        call_pickup_row = self.add_pickup(name='Jôhn')

        call_pickup = call_pickup_dao.get_by(name='Jôhn')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.name, equal_to('Jôhn'))

    def test_get_by_description(self):
        call_pickup_row = self.add_pickup(description='found')

        call_pickup = call_pickup_dao.get_by(description='found')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.description, equal_to('found'))

    def test_get_by_enabled(self):
        call_pickup_row = self.add_pickup(enabled=False)

        call_pickup = call_pickup_dao.get_by(enabled=False)

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.enabled, equal_to(False))

    def test_given_call_pickup_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, call_pickup_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        call_pickup_row = self.add_pickup()
        self.assertRaises(
            NotFoundError,
            call_pickup_dao.get_by, id=call_pickup_row.id, tenant_uuids=[tenant.uuid],
        )

        call_pickup_row = self.add_pickup(tenant_uuid=tenant.uuid)
        call_pickup = call_pickup_dao.get_by(id=call_pickup_row.id, tenant_uuids=[tenant.uuid])
        assert_that(call_pickup, equal_to(call_pickup_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_call_pickups(self):
        result = call_pickup_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        call_pickup1 = self.add_pickup(name='bob', enabled=True)
        call_pickup2 = self.add_pickup(name='alice', enabled=True)

        call_pickups = call_pickup_dao.find_all_by(enabled=True)

        assert_that(call_pickups, has_items(
            has_property('id', call_pickup1.id),
            has_property('id', call_pickup2.id),
        ))

    def test_find_all_by_native_column(self):
        call_pickup1 = self.add_pickup(name='bob', description='description')
        call_pickup2 = self.add_pickup(name='alice', description='description')

        call_pickups = call_pickup_dao.find_all_by(description='description')

        assert_that(call_pickups, has_items(
            has_property('id', call_pickup1.id),
            has_property('id', call_pickup2.id),
        ))

    def test_find_all_by_multi_tenant(self):
        tenant = self.add_tenant()

        call_pickup1 = self.add_pickup(description='description', tenant_uuid=tenant.uuid)
        call_pickup2 = self.add_pickup(description='description')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        call_pickups = call_pickup_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(call_pickups, has_items(call_pickup1, call_pickup2))

        tenants = [tenant.uuid]
        call_pickups = call_pickup_dao.find_all_by(description='description', tenant_uuids=tenants)
        assert_that(call_pickups, all_of(has_items(call_pickup1), not_(has_items(call_pickup2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = call_pickup_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_call_pickups_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_call_pickup_then_returns_one_result(self):
        call_pickup = self.add_pickup(name='bob')
        expected = SearchResult(1, [call_pickup])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        call_pickup1 = self.add_pickup(name='a')
        call_pickup2 = self.add_pickup(name='b', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [call_pickup1, call_pickup2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [call_pickup2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleCallPickups(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.call_pickup1 = self.add_pickup(
            name='Ashton',
            description='resto',
        )
        self.call_pickup2 = self.add_pickup(name='Beaugarton', description='bar')
        self.call_pickup3 = self.add_pickup(name='Casa', description='resto')
        self.call_pickup4 = self.add_pickup(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.call_pickup2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.call_pickup1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.call_pickup2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.call_pickup1, self.call_pickup3, self.call_pickup4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.call_pickup1,
            self.call_pickup2,
            self.call_pickup3,
            self.call_pickup4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.call_pickup4,
            self.call_pickup3,
            self.call_pickup2,
            self.call_pickup1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_pickup1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_pickup2, self.call_pickup3, self.call_pickup4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.call_pickup2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            skip=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        call_pickup_model = CallPickup(name='name', tenant_uuid=self.default_tenant.uuid)

        call_pickup = call_pickup_dao.create(call_pickup_model)

        self.session.expire_all()
        assert_that(inspect(call_pickup).persistent)
        assert_that(call_pickup, has_properties(
            name='name',
            tenant_uuid=self.default_tenant.uuid,
            description=none(),
            enabled=True,
        ))

    def test_create_with_all_fields(self):
        call_pickup_model = CallPickup(
            name='name',
            tenant_uuid=self.default_tenant.uuid,
            description='description',
            enabled=False,
        )

        call_pickup = call_pickup_dao.create(call_pickup_model)

        self.session.expire_all()
        assert_that(inspect(call_pickup).persistent)
        assert_that(call_pickup, has_properties(
            name='name',
            tenant_uuid=self.default_tenant.uuid,
            description='description',
            enabled=False,
        ))

    def test_create_fill_default_values(self):
        self.entity = self.add_entity(tenant_uuid=self.default_tenant.uuid)
        call_pickup_model_1 = CallPickup(name='name1', tenant_uuid=self.default_tenant.uuid)
        call_pickup_model_2 = CallPickup(name='name2', tenant_uuid=self.default_tenant.uuid)

        call_pickup_1 = call_pickup_dao.create(call_pickup_model_1)
        call_pickup_2 = call_pickup_dao.create(call_pickup_model_2)

        assert_that(call_pickup_1, has_properties(
            entity_id=self.entity.id,
            id=1,
        ))
        assert_that(call_pickup_2, has_properties(
            entity_id=self.entity.id,
            id=2,
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        call_pickup = self.add_pickup(
            name='name',
            description='description',
            enabled=True,
        )

        call_pickup = call_pickup_dao.get(call_pickup.id)
        call_pickup.name = 'other_name'
        call_pickup.description = 'other_description'
        call_pickup.enabled = False

        call_pickup_dao.edit(call_pickup)

        self.session.expire_all()
        assert_that(call_pickup, has_properties(
            name='other_name',
            description='other_description',
            enabled=False,
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        call_pickup = self.add_pickup()

        call_pickup_dao.delete(call_pickup)

        assert_that(inspect(call_pickup).deleted)


class TestAssociateUserTargets(DAOTestCase):

    def test_associate(self):
        call_pickup = self.add_pickup()
        user = self.add_user()

        call_pickup_dao.associate_target_users(call_pickup, [user])

        self.session.expire_all()
        assert_that(call_pickup.user_targets, contains_inanyorder(user))

    def test_associate_multiple(self):
        call_pickup = self.add_pickup()
        user1 = self.add_user()
        user2 = self.add_user()

        call_pickup_dao.associate_target_users(call_pickup, [user1, user2])

        self.session.expire_all()
        assert_that(call_pickup.user_targets, contains_inanyorder(user1, user2))

    def test_dissociate(self):
        call_pickup = self.add_pickup()
        user = self.add_user()
        call_pickup_dao.associate_target_users(call_pickup, [user])

        call_pickup_dao.associate_target_users(call_pickup, [])

        self.session.expire_all()
        assert_that(call_pickup.user_targets, empty())

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())


class TestAssociateUserInterceptors(DAOTestCase):

    def test_associate(self):
        call_pickup = self.add_pickup()
        user = self.add_user()

        call_pickup_dao.associate_interceptor_users(call_pickup, [user])

        self.session.expire_all()
        assert_that(call_pickup.user_interceptors, contains_inanyorder(user))

    def test_associate_multiple(self):
        call_pickup = self.add_pickup()
        user1 = self.add_user()
        user2 = self.add_user()

        call_pickup_dao.associate_interceptor_users(call_pickup, [user1, user2])

        self.session.expire_all()
        assert_that(call_pickup.user_interceptors, contains_inanyorder(user1, user2))

    def test_dissociate(self):
        call_pickup = self.add_pickup()
        user = self.add_user()
        call_pickup_dao.associate_interceptor_users(call_pickup, [user])

        call_pickup_dao.associate_interceptor_users(call_pickup, [])

        self.session.expire_all()
        assert_that(call_pickup.user_interceptors, empty())

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())


class TestAssociateGroupTargets(DAOTestCase):

    def test_associate(self):
        call_pickup = self.add_pickup()
        group = self.add_group()

        call_pickup_dao.associate_target_groups(call_pickup, [group])

        self.session.expire_all()
        assert_that(call_pickup.group_targets, contains_inanyorder(group))

    def test_associate_multiple(self):
        call_pickup = self.add_pickup()
        group1 = self.add_group()
        group2 = self.add_group()

        call_pickup_dao.associate_target_groups(call_pickup, [group1, group2])

        self.session.expire_all()
        assert_that(call_pickup.group_targets, contains_inanyorder(group1, group2))

    def test_dissociate(self):
        call_pickup = self.add_pickup()
        group = self.add_group()
        call_pickup_dao.associate_target_groups(call_pickup, [group])

        call_pickup_dao.associate_target_groups(call_pickup, [])

        self.session.expire_all()
        assert_that(call_pickup.group_targets, empty())

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())


class TestAssociateGroupInterceptors(DAOTestCase):

    def test_associate(self):
        call_pickup = self.add_pickup()
        group = self.add_group()

        call_pickup_dao.associate_interceptor_groups(call_pickup, [group])

        self.session.expire_all()
        assert_that(call_pickup.group_interceptors, contains_inanyorder(group))

    def test_associate_multiple(self):
        call_pickup = self.add_pickup()
        group1 = self.add_group()
        group2 = self.add_group()

        call_pickup_dao.associate_interceptor_groups(call_pickup, [group1, group2])

        self.session.expire_all()
        assert_that(call_pickup.group_interceptors, contains_inanyorder(group1, group2))

    def test_dissociate(self):
        call_pickup = self.add_pickup()
        group = self.add_group()
        call_pickup_dao.associate_interceptor_groups(call_pickup, [group])

        call_pickup_dao.associate_interceptor_groups(call_pickup, [])

        self.session.expire_all()
        assert_that(call_pickup.group_interceptors, empty())

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())
