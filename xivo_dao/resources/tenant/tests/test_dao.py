# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult

from .. import dao


UNKNOWN_UUID = str(uuid.uuid4())


class TestFind(DAOTestCase):

    def test_find_no_resources(self):
        result = dao.find(UNKNOWN_UUID)

        assert_that(result, none())

    def test_find(self):
        tenant_row = self.add_tenant()

        tenant = dao.find(tenant_row.uuid)

        assert_that(tenant, equal_to(tenant_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()

        result = dao.find(tenant.uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(tenant))

        result = dao.find(tenant.uuid, tenant_uuids=[UNKNOWN_UUID])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_resource(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)

    def test_get(self):
        row = self.add_tenant()

        resource = dao.get(row.uuid)

        assert_that(resource, equal_to(row))

    def test_get_multi_tenant(self):
        row = self.add_tenant()
        resource = dao.get(row.uuid, tenant_uuids=[row.uuid])
        assert_that(resource, equal_to(row))

        self.assertRaises(NotFoundError, dao.get, row.uuid, tenant_uuids=[UNKNOWN_UUID])


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, dao.find_by, invalid=42)

    def test_find_by_uuid(self):
        row = self.add_tenant()

        resource = dao.find_by(uuid=row.uuid)

        assert_that(resource, equal_to(row))
        assert_that(resource.uuid, equal_to(row.uuid))

    def test_given_resource_does_not_exist_then_returns_null(self):
        resource = dao.find_by(uuid=UNKNOWN_UUID)

        assert_that(resource, none())

    def test_find_by_multi_tenant(self):
        row = self.add_tenant()
        resource = dao.find_by(uuid=row.uuid, tenant_uuids=[UNKNOWN_UUID])
        assert_that(resource, none())

        resource = dao.find_by(uuid=row.uuid, tenant_uuids=[row.uuid])
        assert_that(resource, equal_to(row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, dao.get_by, invalid=42)

    def test_get_by_uuid(self):
        row = self.add_tenant()

        resource = dao.get_by(uuid=row.uuid)

        assert_that(resource, equal_to(row))
        assert_that(resource.uuid, equal_to(resource.uuid))

    def test_given_resource_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get_by, uuid=UNKNOWN_UUID)

    def test_get_by_multi_tenant(self):
        row = self.add_tenant()
        self.assertRaises(
            NotFoundError,
            dao.get_by, uuid=row.uuid, tenant_uuids=[UNKNOWN_UUID],
        )

        resource = dao.get_by(uuid=row.uuid, tenant_uuids=[row.uuid])
        assert_that(resource, equal_to(row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_resource(self):
        result = dao.find_all_by(uuid=UNKNOWN_UUID)

        assert_that(result, contains())

    def test_find_all_by_multi_tenant(self):
        row = self.add_tenant()

        resources = dao.find_all_by(uuid=row.uuid, tenant_uuids=[row.uuid])
        assert_that(resources, has_items(row))

        resources = dao.find_all_by(uuid=row.uuid, tenant_uuids=[UNKNOWN_UUID])
        assert_that(resources, contains())


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_resource_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected, tenant_uuids=[])

    def test_given_one_resource_then_returns_one_result(self):
        resource = self.add_tenant()
        expected = SearchResult(1, [resource])

        self.assert_search_returns_result(expected, tenant_uuids=[resource.uuid])
