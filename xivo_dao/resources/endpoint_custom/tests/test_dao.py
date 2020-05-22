# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    equal_to,
    has_items,
    has_properties,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as custom_dao


class TestGet(DAOTestCase):

    def test_get_no_sccp(self):
        self.assertRaises(NotFoundError, custom_dao.get, 42)

    def test_get(self):
        custom_row = self.add_usercustom(interface='custom/get')

        custom = custom_dao.get(custom_row.id)

        assert_that(custom, equal_to(custom_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        custom_row = self.add_usercustom(tenant_uuid=tenant.uuid)
        custom = custom_dao.get(custom_row.id, tenant_uuids=[tenant.uuid])
        assert_that(custom, equal_to(custom_row))

        custom_row = self.add_usercustom()
        self.assertRaises(
            NotFoundError,
            custom_dao.get, custom_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, custom_dao.find_by, invalid=42)

    def test_given_row_with_value_does_not_exist_then_returns_null(self):
        result = custom_dao.find_by(interface='abcd')
        assert_that(result, none())

    def test_find_by(self):
        custom_row = self.add_usercustom(interface='custom/custom')

        custom = custom_dao.find_by(interface='custom/custom')

        assert_that(custom, equal_to(custom_row))

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        custom_row = self.add_usercustom()
        custom = custom_dao.find_by(name=custom_row.name, tenant_uuids=[tenant.uuid])
        assert_that(custom, none())

        custom_row = self.add_usercustom(tenant_uuid=tenant.uuid)
        custom = custom_dao.find_by(name=custom_row.name, tenant_uuids=[tenant.uuid])
        assert_that(custom, equal_to(custom_row))


class TestFindAllBy(DAOTestCase):

    def test_given_column_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, custom_dao.find_all_by, invalid=42)

    def test_given_row_with_value_does_not_exist_then_returns_empty_list(self):
        result = custom_dao.find_all_by(interface='abcd')
        assert_that(result, empty())

    def test_find_all_by(self):
        custom_row = self.add_usercustom(interface='custom/interface')
        self.add_usercustom(interface='sip/interface')

        custom = custom_dao.find_all_by(interface='custom/interface')

        assert_that(custom, contains(custom_row))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        custom1 = self.add_usercustom(context='default', tenant_uuid=tenant.uuid)
        custom2 = self.add_usercustom(context='default')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        customs = custom_dao.find_all_by(context='default', tenant_uuids=tenants)
        assert_that(customs, has_items(custom1, custom2))

        tenants = [tenant.uuid]
        customs = custom_dao.find_all_by(context='default', tenant_uuids=tenants)
        assert_that(customs, all_of(has_items(custom1), not_(has_items(custom2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = custom_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_search(self):
        custom = self.add_usercustom()
        expected = SearchResult(1, [custom])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        custom1 = self.add_usercustom(interface='custom/sort1')
        custom2 = self.add_usercustom(interface='custom/sort2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [custom1, custom2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [custom2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        custom = custom_dao.create(
            Custom(
                interface='custom/create',
                tenant_uuid=self.default_tenant.uuid
            )
        )

        assert_that(inspect(custom).persistent)
        assert_that(custom, has_properties(
            id=not_none(),
            interface='custom/create',
            enabled=True,
            name=none(),
            commented=0,
            protocol='custom',
            category='user',
        ))

    def test_create_all_parameters(self):
        custom = custom_dao.create(
            Custom(
                interface='custom/create',
                enabled=False,
                tenant_uuid=self.default_tenant.uuid
            )
        )

        assert_that(inspect(custom).persistent)
        assert_that(custom, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            interface='custom/create',
            enabled=False,
            name=none(),
            commented=1,
            protocol='custom',
            category='user',
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_parameters(self):
        custom = self.add_usercustom(interface='custom/beforeedit', enabled=True)

        self.session.expire_all()
        custom.interface = 'custom/afteredit'
        custom.enabled = True

        custom_dao.edit(custom)

        self.session.expire_all()
        assert_that(custom, has_properties(
            interface='custom/afteredit',
            enabled=True,
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        custom = self.add_usercustom()

        custom_dao.delete(custom)

        assert_that(inspect(custom).deleted)

    def test_given_line_associated_to_custom_when_deleted_then_line_dissociated(self):
        custom = self.add_usercustom(context='default')
        line = self.add_line(
            context='default',
            name='1000',
            number='1000',
            endpoint_custom_id=custom.id,
        )

        custom_dao.delete(custom)

        assert_that(line, has_properties(endpoint_custom_id=none()))


class TestRelations(DAOTestCase):

    # TODO should be in test_trunkfeatures
    def test_trunk_relationship(self):
        custom = self.add_usercustom()
        trunk = self.add_trunk(endpoint_custom_id=custom.id)

        self.session.flush()

        self.session.expire_all()
        assert_that(custom.trunk, equal_to(trunk))

    # TODO should be in test_linefeatures
    def test_line_relationship(self):
        custom = self.add_usercustom()
        line = self.add_line(endpoint_custom_id=custom.id)

        self.session.flush()

        self.session.expire_all()
        assert_that(custom.line, equal_to(line))
