# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.external_app import ExternalApp
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.external_app import dao as external_app_dao
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase


class TestFind(DAOTestCase):
    def test_find_no_external_app(self):
        result = external_app_dao.find('42')

        assert_that(result, none())

    def test_find(self):
        external_app_row = self.add_external_app()

        external_app = external_app_dao.find(external_app_row.name)

        assert_that(external_app, equal_to(external_app_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        external_app = self.add_external_app(tenant_uuid=tenant.uuid)

        result = external_app_dao.find(external_app.name, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(external_app))

        result = external_app_dao.find(
            external_app.name, tenant_uuids=[self.default_tenant.uuid]
        )
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_external_app(self):
        self.assertRaises(NotFoundError, external_app_dao.get, '42')

    def test_get(self):
        external_app_row = self.add_external_app()

        external_app = external_app_dao.get(external_app_row.name)

        assert_that(external_app.name, equal_to(external_app.name))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        external_app_row = self.add_external_app(tenant_uuid=tenant.uuid)
        external_app = external_app_dao.get(
            external_app_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(external_app, equal_to(external_app_row))

        external_app_row = self.add_external_app()
        self.assertRaises(
            NotFoundError,
            external_app_dao.get,
            external_app_row.name,
            tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, external_app_dao.find_by, invalid=42)

    def test_find_by_name(self):
        external_app_row = self.add_external_app(name='123')

        external_app = external_app_dao.find_by(name='123')

        assert_that(external_app, equal_to(external_app_row))
        assert_that(external_app.name, equal_to('123'))

    def test_given_external_app_does_not_exist_then_returns_null(self):
        external_app = external_app_dao.find_by(name='42')

        assert_that(external_app, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        external_app_row = self.add_external_app()
        external_app = external_app_dao.find_by(
            name=external_app_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(external_app, none())

        external_app_row = self.add_external_app(tenant_uuid=tenant.uuid)
        external_app = external_app_dao.find_by(
            name=external_app_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(external_app, equal_to(external_app_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, external_app_dao.get_by, invalid=42)

    def test_get_by_name(self):
        external_app_row = self.add_external_app(name='123')

        external_app = external_app_dao.get_by(name='123')

        assert_that(external_app, equal_to(external_app_row))
        assert_that(external_app.name, equal_to('123'))

    def test_given_external_app_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, external_app_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        external_app_row = self.add_external_app()
        self.assertRaises(
            NotFoundError,
            external_app_dao.get_by,
            name=external_app_row.name,
            tenant_uuids=[tenant.uuid],
        )

        external_app_row = self.add_external_app(tenant_uuid=tenant.uuid)
        external_app = external_app_dao.get_by(
            name=external_app_row.name, tenant_uuids=[tenant.uuid]
        )
        assert_that(external_app, equal_to(external_app_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_external_apps(self):
        result = external_app_dao.find_all_by(name='123')

        assert_that(result, contains_exactly())

    def test_find_all_by_native_column(self):
        tenant1 = self.add_tenant()
        tenant2 = self.add_tenant()
        external_app1 = self.add_external_app(
            name='external_app', tenant_uuid=tenant1.uuid
        )
        external_app2 = self.add_external_app(
            name='external_app', tenant_uuid=tenant2.uuid
        )

        external_apps = external_app_dao.find_all_by(name='external_app')

        assert_that(
            external_apps,
            has_items(
                has_property('name', external_app1.name),
                has_property('name', external_app2.name),
            ),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        external_app1 = self.add_external_app(name='name', tenant_uuid=tenant.uuid)
        external_app2 = self.add_external_app(name='name')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        external_apps = external_app_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(external_apps, has_items(external_app1, external_app2))

        tenants = [tenant.uuid]
        external_apps = external_app_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(
            external_apps,
            all_of(has_items(external_app1), not_(has_items(external_app2))),
        )


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = external_app_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_external_apps_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_external_app_then_returns_one_result(self):
        external_app = self.add_external_app()
        expected = SearchResult(1, [external_app])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        external_app1 = self.add_external_app(name='1')
        external_app2 = self.add_external_app(name='2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [external_app1, external_app2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [external_app2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleExternalApps(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.external_app1 = self.add_external_app(name='Ashton')
        self.external_app2 = self.add_external_app(name='Beaugarton')
        self.external_app3 = self.add_external_app(name='Casa')
        self.external_app4 = self.add_external_app(name='Dunkin')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.external_app2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.external_app1])
        self.assert_search_returns_result(expected_resto, search='ton', name='Ashton')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.external_app2])
        self.assert_search_returns_result(expected_allow, name='Beaugarton')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.external_app1,
                self.external_app2,
                self.external_app3,
                self.external_app4,
            ],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.external_app4,
                self.external_app3,
                self.external_app2,
                self.external_app1,
            ],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.external_app1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(
            4, [self.external_app2, self.external_app3, self.external_app4]
        )

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.external_app2])

        self.assert_search_returns_result(
            expected,
            search='a',
            order='name',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):
    def test_create_minimal_fields(self):
        external_app_model = ExternalApp(
            tenant_uuid=self.default_tenant.uuid,
            name='required',
        )
        external_app = external_app_dao.create(external_app_model)

        self.session.expire_all()
        assert_that(inspect(external_app).persistent)
        assert_that(
            external_app,
            has_properties(
                tenant_uuid=self.default_tenant.uuid,
                configuration=None,
            ),
        )

    def test_create_with_all_fields(self):
        external_app_model = ExternalApp(
            tenant_uuid=self.default_tenant.uuid,
            name='external_app',
            label='External App',
            configuration={'key': {'subkey': 'value'}},
        )
        external_app = external_app_dao.create(external_app_model)

        self.session.expire_all()
        assert_that(inspect(external_app).persistent)
        assert_that(
            external_app,
            has_properties(
                name='external_app',
                label='External App',
                tenant_uuid=self.default_tenant.uuid,
                configuration={'key': {'subkey': 'value'}},
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        external_app = self.add_external_app(
            name='external_app',
            label='External App',
            configuration={'original': 'data'},
        )

        self.session.expire_all()
        external_app.name = 'other_external_app'
        external_app.label = 'External App Label'
        external_app.configuration = {'edited': 'data'}

        external_app_dao.edit(external_app)

        self.session.expire_all()
        assert_that(
            external_app,
            has_properties(
                name='other_external_app',
                label='External App Label',
                configuration={'edited': 'data'},
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        external_app = self.add_external_app()

        external_app_dao.delete(external_app)

        assert_that(inspect(external_app).deleted)
