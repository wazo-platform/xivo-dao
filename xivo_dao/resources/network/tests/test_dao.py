# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
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
    raises
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.network import Network
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult

from .. import dao

UNKNOWN_UUID = uuid.uuid4()


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_raise_error(self):
        self.assertRaises(InputError, dao.find_by, column=1)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = dao.find_by(public_hostname='unknown')
        assert_that(result, none())

    def test_find_by(self):
        network = self.add_network(public_hostname='known')
        result = dao.find_by(public_hostname='known')

        assert_that(result.uuid, equal_to(network.uuid))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_network()
        resource = dao.find_by(public_hostname=row.public_hostname, tenant_uuids=[tenant.uuid])
        assert_that(resource, none())

        row = self.add_network(tenant_uuid=tenant.uuid)
        resource = dao.find_by(public_hostname=row.public_hostname, tenant_uuids=[tenant.uuid])
        assert_that(resource, equal_to(row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        resource1 = self.add_network(public_hostname='my network', tenant_uuid=tenant.uuid)
        resource2 = self.add_network(public_hostname='my network')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        networks = dao.find_all_by(public_hostname='my network', tenant_uuids=tenants)
        assert_that(networks, has_items(resource1, resource2))

        tenants = [tenant.uuid]
        meetings = dao.find_all_by(public_hostname='my network', tenant_uuids=tenants)
        assert_that(meetings, all_of(has_items(resource1), not_(has_items(resource2))))


class TestGet(DAOTestCase):

    def test_given_no_rows_then_raises_error(self):
        self.assertRaises(NotFoundError, dao.get, UNKNOWN_UUID)
        self.assertRaises(NotFoundError, dao.get, str(UNKNOWN_UUID))

    def test_given_row_with_minimal_parameters_then_returns_model(self):
        row = self.add_network()

        model = dao.get(row.uuid)
        assert_that(isinstance(row.uuid, uuid.UUID), equal_to(True))
        assert_that(model, has_properties(
            public_hostname=row.public_hostname,
            uuid=row.uuid,
        ))

        model = dao.get(str(row.uuid))
        assert_that(model, has_properties(
            public_hostname=row.public_hostname,
            uuid=row.uuid,
        ))

    def test_given_row_with_all_parameters_then_returns_model(self):
        row = self.add_network(
            public_hostname='hostname',
            public_port=10443,
            public_https=False,
            tenant_uuid=self.default_tenant.uuid,
        )

        model = dao.get(row.uuid)
        assert_that(model, has_properties(
            public_hostname='hostname',
            public_port=10443,
            public_https=False,
            tenant_uuid=self.default_tenant.uuid,
        ))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        row = self.add_network(tenant_uuid=tenant.uuid)
        model = dao.get(row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(model, equal_to(row))

        row = self.add_network()
        self.assertRaises(
            NotFoundError,
            dao.get, row.uuid, tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_sip_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_network_then_returns_one_result(self):
        model = self.add_network()
        expected = SearchResult(1, [model])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        model_1 = self.add_network(public_hostname='sort1')
        model_2 = self.add_network(public_hostname='sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [model_1, model_2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [model_2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleNetworks(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()
        tenant_3 = self.add_tenant()
        self.network1 = self.add_network(public_hostname='Ashton')
        self.network2 = self.add_network(public_hostname='Beaugarton', tenant_uuid=tenant_1.uuid)
        self.network3 = self.add_network(public_hostname='Casa', tenant_uuid=tenant_2.uuid)
        self.network4 = self.add_network(public_hostname='Dunkin', tenant_uuid=tenant_3.uuid)

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.network2])

        self.assert_search_returns_result(expected, search='eau', recurse=True)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.network1,
            self.network2,
            self.network3,
            self.network4,
        ])

        self.assert_search_returns_result(expected, order='public_hostname', recurse=True)

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.network4,
            self.network3,
            self.network2,
            self.network1,
        ])

        self.assert_search_returns_result(expected, order='public_hostname', direction='desc', recurse=True)

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.network1])

        self.assert_search_returns_result(expected, limit=1, recurse=True)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.network2, self.network3, self.network4])

        self.assert_search_returns_result(expected, offset=1, recurse=True)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.network2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='public_hostname',
            direction='desc',
            offset=1,
            limit=1,
            recurse=True,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        model = Network(public_hostname='hostname', tenant_uuid=self.default_tenant.uuid)

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(result, has_properties(
            uuid=not_none(),
            public_hostname='hostname',
            public_port=None,
            public_https=None,
            tenant_uuid=self.default_tenant.uuid,
        ))

    def test_create_all_parameters(self):
        model = Network(
            tenant_uuid=self.default_tenant.uuid,
            public_hostname='name',
            public_port=10443,
            public_https=False,
        )

        result = dao.create(model)

        assert_that(inspect(result).persistent)
        assert_that(result, has_properties(
            uuid=not_none(),
            public_hostname='name',
            public_port=10443,
            public_https=False,
            tenant_uuid=self.default_tenant.uuid,
        ))

    def test_that_only_one_config_can_exist_in_a_tenant(self):
        model_1 = Network(
            public_hostname='one',
            tenant_uuid=self.default_tenant.uuid,
        )
        dao.create(model_1)

        model_2 = Network(
            public_hostname='two',
            tenant_uuid=self.default_tenant.uuid,
        )
        assert_that(
            calling(dao.create).with_args(model_2),
            raises(IntegrityError),
        )


class TestEdit(DAOTestCase):

    def test_edit_all_parameters(self):
        row = self.add_network()

        model = dao.get(row.uuid)
        model.public_hostname = 'new'
        model.public_port = 10443
        model.public_https = False

        dao.edit(model)

        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                public_hostname='new',
                public_port=10443,
                public_https=False,
            )
        )

    def test_edit_set_null(self):
        row = self.add_network(
            public_port=10443,
            public_https=False,
        )

        model = dao.get(row.uuid)
        model.public_port = 443
        model.public_https = True

        dao.edit(model)
        self.session.expire_all()
        assert_that(
            model,
            has_properties(
                uuid=model.uuid,
                public_port=443,
                public_https=True,
            )
        )


class TestDelete(DAOTestCase):

    def test_delete(self):
        model = self.add_network()

        dao.delete(model)

        assert_that(inspect(model).deleted)
