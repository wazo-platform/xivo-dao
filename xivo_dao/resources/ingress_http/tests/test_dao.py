# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from hamcrest import (
    all_of,
    assert_that,
    calling,
    equal_to,
    has_items,
    has_properties,
    none,
    not_,
    not_none,
    raises,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.ingress_http import IngressHTTP
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult

from .. import dao

UNKNOWN_UUID = uuid.uuid4()


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_raise_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = dao.find_by(uri='http://unknown')
        assert_that(result, none())

    def test_find_by(self):
        ingress_http = self.add_ingress_http(uri='http://known')
        result = dao.find_by(uri='http://known')

        assert_that(result.uuid, equal_to(ingress_http.uuid))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_ingress_http()
        resource = dao.find_by(uri=row.uri, tenant_uuids=[tenant.uuid])
        assert_that(resource, none())

        row = self.add_ingress_http(tenant_uuid=tenant.uuid)
        resource = dao.find_by(uri=row.uri, tenant_uuids=[tenant.uuid])
        assert_that(resource, equal_to(row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        resource1 = self.add_ingress_http(
            uri='my ingress_http', tenant_uuid=tenant.uuid
        )
        resource2 = self.add_ingress_http(uri='my ingress_http')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        ingresses_http = dao.find_all_by(uri='my ingress_http', tenant_uuids=tenants)
        assert_that(ingresses_http, has_items(resource1, resource2))

        tenants = [tenant.uuid]
        meetings = dao.find_all_by(uri='my ingress_http', tenant_uuids=tenants)
        assert_that(meetings, all_of(has_items(resource1), not_(has_items(resource2))))


class TestGet(DAOTestCase):
    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)
        self.assertRaises(NotFoundError, dao.get, str(UNKNOWN_UUID))

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_ingress_http()

        model = dao.get(row.uuid)
        assert_that(isinstance(row.uuid, uuid.UUID), equal_to(True))
        assert_that(
            model,
            has_properties(
                uri=row.uri,
                uuid=row.uuid,
            ),
        )

        model = dao.get(str(row.uuid))
        assert_that(
            model,
            has_properties(
                uri=row.uri,
                uuid=row.uuid,
            ),
        )

    def test_given_row_with_all_parameters_then_returns_model(self):
        row = self.add_ingress_http(
            uri='http://hostname:10080',
            tenant_uuid=self.default_tenant.uuid,
        )

        model = dao.get(row.uuid)
        assert_that(
            model,
            has_properties(
                uri='http://hostname:10080',
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_ingress_http(tenant_uuid=tenant.uuid)
        model = dao.get(row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(model, equal_to(row))

        row = self.add_ingress_http()
        self.assertRaises(
            NotFoundError,
            dao.get,
            row.uuid,
            tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_ingress_http_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_ingress_http_then_returns_one_result(self):
        model = self.add_ingress_http()
        expected = SearchResult(1, [model])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        model_1 = self.add_ingress_http(uri='sort1')
        model_2 = self.add_ingress_http(uri='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [model_1, model_2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [model_2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleHTTPIngresses(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()
        tenant_3 = self.add_tenant()
        self.ingress_http1 = self.add_ingress_http(uri='Ashton')
        self.ingress_http2 = self.add_ingress_http(
            uri='Beaugarton', tenant_uuid=tenant_1.uuid
        )
        self.ingress_http3 = self.add_ingress_http(
            uri='Casa', tenant_uuid=tenant_2.uuid
        )
        self.ingress_http4 = self.add_ingress_http(
            uri='Dunkin', tenant_uuid=tenant_3.uuid
        )

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.ingress_http2])

        self.assert_search_returns_result(expected, search='eau', recurse=True)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.ingress_http1,
                self.ingress_http2,
                self.ingress_http3,
                self.ingress_http4,
            ],
        )

        self.assert_search_returns_result(expected, order='uri', recurse=True)

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.ingress_http4,
                self.ingress_http3,
                self.ingress_http2,
                self.ingress_http1,
            ],
        )

        self.assert_search_returns_result(
            expected, order='uri', direction='desc', recurse=True
        )

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.ingress_http1])

        self.assert_search_returns_result(expected, limit=1, recurse=True)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(
            4, [self.ingress_http2, self.ingress_http3, self.ingress_http4]
        )

        self.assert_search_returns_result(expected, offset=1, recurse=True)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.ingress_http2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='uri',
            direction='desc',
            offset=1,
            limit=1,
            recurse=True,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_parameters(self):
        model = IngressHTTP(uri='http://hostname', tenant_uuid=self.default_tenant.uuid)

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                uri='http://hostname',
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_create_all_parameters(self):
        model = IngressHTTP(
            tenant_uuid=self.default_tenant.uuid,
            uri='https://name',
        )

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(
            result,
            has_properties(
                uuid=not_none(),
                uri='https://name',
                tenant_uuid=self.default_tenant.uuid,
            ),
        )

    def test_that_only_one_config_can_exist_in_a_tenant(self):
        model_1 = IngressHTTP(
            uri='https://one',
            tenant_uuid=self.default_tenant.uuid,
        )
        dao.create(model_1)

        model_2 = IngressHTTP(
            uri='https://two',
            tenant_uuid=self.default_tenant.uuid,
        )
        assert_that(
            calling(dao.create).with_args(model_2),
            raises(IntegrityError),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_parameters(self):
        row = self.add_ingress_http()

        model = dao.get(row.uuid)
        model.uri = 'https://new'

        dao.edit(model)

        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                uri='https://new',
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        model = self.add_ingress_http()

        dao.delete(model)

        assert_that(inspect(model).deleted)
