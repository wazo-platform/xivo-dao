# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
    not_,
)

from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as switchboard_dao


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = switchboard_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_switchboards_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_switchboard_then_returns_one_result(self):
        switchboard = self.add_switchboard()
        expected = SearchResult(1, [switchboard])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        switchboard1 = self.add_switchboard(name='a')
        switchboard2 = self.add_switchboard(name='b', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [switchboard1, switchboard2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [switchboard2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleSwitchboards(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.switchboard1 = self.add_switchboard(name='Ashton')
        self.switchboard2 = self.add_switchboard(name='Beaugarton')
        self.switchboard3 = self.add_switchboard(name='Casa')
        self.switchboard4 = self.add_switchboard(name='Dunkin')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.switchboard2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.switchboard1,
            self.switchboard2,
            self.switchboard3,
            self.switchboard4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.switchboard4,
            self.switchboard3,
            self.switchboard2,
            self.switchboard1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.switchboard1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.switchboard2, self.switchboard3, self.switchboard4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.switchboard2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestGet(DAOTestCase):

    def test_get_no_switchboard(self):
        self.assertRaises(NotFoundError, switchboard_dao.get, 42)

    def test_get(self):
        switchboard_row = self.add_switchboard()

        switchboard = switchboard_dao.get(switchboard_row.uuid)

        assert_that(switchboard.uuid, equal_to(switchboard.uuid))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        switchboard_row = self.add_switchboard(tenant_uuid=tenant.uuid)
        switchboard = switchboard_dao.get(switchboard_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(switchboard, equal_to(switchboard_row))

        switchboard_row = self.add_switchboard()
        self.assertRaises(
            NotFoundError,
            switchboard_dao.get, switchboard_row.uuid, tenant_uuids=[tenant.uuid],
        )


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, switchboard_dao.get_by, invalid=42)

    def test_get_by_name(self):
        switchboard_row = self.add_switchboard(name='switchboard')

        switchboard = switchboard_dao.get_by(name='switchboard')

        assert_that(switchboard, equal_to(switchboard_row))
        assert_that(switchboard.name, equal_to('switchboard'))

    def test_given_switchboard_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, switchboard_dao.get_by, name='not-found')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        switchboard_row = self.add_switchboard()
        self.assertRaises(
            NotFoundError,
            switchboard_dao.get_by, uuid=switchboard_row.uuid, tenant_uuids=[tenant.uuid],
        )

        switchboard_row = self.add_switchboard(tenant_uuid=tenant.uuid)
        switchboard = switchboard_dao.get_by(uuid=switchboard_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(switchboard, equal_to(switchboard_row))


class TestFind(DAOTestCase):

    def test_find_no_switchboard(self):
        result = switchboard_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        switchboard_row = self.add_switchboard()

        switchboard = switchboard_dao.find(switchboard_row.uuid)

        assert_that(switchboard, equal_to(switchboard_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        switchboard = self.add_switchboard(tenant_uuid=tenant.uuid)

        result = switchboard_dao.find(switchboard.uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(switchboard))

        result = switchboard_dao.find(switchboard.uuid, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, switchboard_dao.find_by, invalid=42)

    def test_find_by_name(self):
        switchboard_row = self.add_switchboard(name='switchboard')

        switchboard = switchboard_dao.find_by(name='switchboard')

        assert_that(switchboard, equal_to(switchboard_row))
        assert_that(switchboard.name, equal_to('switchboard'))

    def test_given_switchboard_does_not_exist_then_returns_null(self):
        switchboard = switchboard_dao.find_by(name='not-found')

        assert_that(switchboard, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        switchboard_row = self.add_switchboard()
        switchboard = switchboard_dao.find_by(uuid=switchboard_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(switchboard, none())

        switchboard_row = self.add_switchboard(tenant_uuid=tenant.uuid)
        switchboard = switchboard_dao.find_by(uuid=switchboard_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(switchboard, equal_to(switchboard_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_switchboards(self):
        result = switchboard_dao.find_all_by(name='switchboard')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        switchboard1 = self.add_switchboard(name='switchboard')
        switchboard2 = self.add_switchboard(name='switchboard')

        switchboards = switchboard_dao.find_all_by(name='switchboard')

        assert_that(switchboards, has_items(
            has_property('uuid', switchboard1.uuid),
            has_property('uuid', switchboard2.uuid),
        ))

    def test_find_all_by_multi_tenant(self):
        tenant = self.add_tenant()

        switchboard1 = self.add_switchboard(name='name', tenant_uuid=tenant.uuid)
        switchboard2 = self.add_switchboard(name='name')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        switchboards = switchboard_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(switchboards, has_items(switchboard1, switchboard2))

        tenants = [tenant.uuid]
        switchboards = switchboard_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(switchboards, all_of(has_items(switchboard1), not_(has_items(switchboard2))))


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        switchboard = Switchboard(name='switchboard', tenant_uuid=self.default_tenant.uuid)

        switchboard = switchboard_dao.create(switchboard)

        self.session.expire_all()
        assert_that(inspect(switchboard).persistent)
        assert_that(switchboard, has_properties(
            uuid=is_not(none()),
            tenant_uuid=self.default_tenant.uuid,
            name='switchboard',
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        switchboard = self.add_switchboard(name='switchboard')

        switchboard.name = 'other_switchboard'
        switchboard_dao.edit(switchboard)

        self.session.expire_all()
        assert_that(switchboard, has_properties(name='other_switchboard'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        switchboard = self.add_switchboard()

        switchboard_dao.delete(switchboard)

        assert_that(inspect(switchboard).deleted)
