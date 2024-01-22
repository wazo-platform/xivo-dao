# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    equal_to,
    has_items,
    has_properties,
    has_property,
    is_not,
    none,
    not_,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.application import Application
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult

from .. import dao as application_dao


class TestFind(DAOTestCase):

    def test_find_no_application(self):
        result = application_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        application_row = self.add_application()

        application = application_dao.find(application_row.uuid)

        assert_that(application, equal_to(application_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        application = self.add_application(tenant_uuid=tenant.uuid)

        result = application_dao.find(application.uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(application))

        result = application_dao.find(application.uuid, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_application(self):
        self.assertRaises(NotFoundError, application_dao.get, 42)

    def test_get(self):
        application_row = self.add_application()

        application = application_dao.get(application_row.uuid)

        assert_that(application, equal_to(application_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        application_row = self.add_application(tenant_uuid=tenant.uuid)
        application = application_dao.get(application_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(application, equal_to(application_row))

        application_row = self.add_application()
        self.assertRaises(
            NotFoundError,
            application_dao.get, application_row.uuid, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, application_dao.find_by, invalid=42)

    def test_find_by_name(self):
        application_row = self.add_application(name='myname')

        application = application_dao.find_by(name='myname')

        assert_that(application, equal_to(application_row))
        assert_that(application.name, equal_to('myname'))

    def test_given_application_does_not_exist_then_returns_null(self):
        application = application_dao.find_by(uuid=42)

        assert_that(application, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        application_row = self.add_application()
        application = application_dao.find_by(name=application_row.name, tenant_uuids=[tenant.uuid])
        assert_that(application, none())

        application_row = self.add_application(tenant_uuid=tenant.uuid)
        application = application_dao.find_by(name=application_row.name, tenant_uuids=[tenant.uuid])
        assert_that(application, equal_to(application_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, application_dao.get_by, invalid=42)

    def test_get_by_name(self):
        application_row = self.add_application(name='myname')

        application = application_dao.get_by(name='myname')

        assert_that(application, equal_to(application_row))
        assert_that(application.name, equal_to('myname'))

    def test_given_application_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, application_dao.get_by, uuid='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        application_row = self.add_application()
        self.assertRaises(
            NotFoundError,
            application_dao.get_by, uuid=application_row.uuid, tenant_uuids=[tenant.uuid],
        )

        application_row = self.add_application(tenant_uuid=tenant.uuid)
        application = application_dao.get_by(uuid=application_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(application, equal_to(application_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_application(self):
        result = application_dao.find_all_by(name='my_name')

        assert_that(result, contains_exactly())

    def test_find_all_by(self):
        application1 = self.add_application(name='MyApplication')
        application2 = self.add_application(name='MyApplication')

        applications = application_dao.find_all_by(name='MyApplication')

        assert_that(applications, has_items(
            has_property('uuid', application1.uuid),
            has_property('uuid', application2.uuid)
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        application1 = self.add_application(name='application', tenant_uuid=tenant.uuid)
        application2 = self.add_application(name='application')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        applications = application_dao.find_all_by(name='application', tenant_uuids=tenants)
        assert_that(applications, has_items(application1, application2))

        tenants = [tenant.uuid]
        applications = application_dao.find_all_by(name='application', tenant_uuids=tenants)
        assert_that(applications, all_of(has_items(application1), not_(has_items(application2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = application_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_application_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_application_then_returns_one_result(self):
        application = self.add_application()
        expected = SearchResult(1, [application])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        application1 = self.add_application(name='1')
        application2 = self.add_application(name='2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [application1, application2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants, order='name')

        expected = SearchResult(1, [application2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        application = Application(tenant_uuid=self.default_tenant.uuid)
        application = application_dao.create(application)

        assert_that(inspect(application).persistent)
        assert_that(
            application,
            has_properties(
                uuid=is_not(none()),
                tenant_uuid=self.default_tenant.uuid,
                name=None,
            )
        )

    def test_create_with_all_fields(self):
        application = Application(name='myApplication', tenant_uuid=self.default_tenant.uuid)
        application = application_dao.create(application)

        assert_that(inspect(application).persistent)
        assert_that(
            application,
            has_properties(
                uuid=is_not(none()),
                tenant_uuid=self.default_tenant.uuid,
                name='myApplication',
            )
        )


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        application = self.add_application(
            name='name',
            tenant_uuid=self.default_tenant.uuid,
        )

        self.session.expire_all()
        application = application_dao.get(application.uuid)
        application.name = 'other_name'

        application_dao.edit(application)

        self.session.expire_all()
        assert_that(application, has_properties(
            uuid=is_not(none()),
            name='other_name',
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        application = self.add_application()

        application_dao.delete(application)

        assert_that(inspect(application).deleted)
