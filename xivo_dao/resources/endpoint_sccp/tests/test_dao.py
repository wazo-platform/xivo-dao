# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    empty,
    equal_to,
    has_items,
    has_properties,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as sccp_dao

ALL_OPTIONS = [
    ["cid_name", "Jôhn Smith"],
    ["cid_num", "5551234567"],
    ["disallow", "all"],
    ["allow", "gsm,g729"],
]


class TestFind(DAOTestCase):

    def test_find_no_sccp(self):
        result = sccp_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        sccp_row = self.add_sccpline()

        sccp = sccp_dao.find(sccp_row.id)

        assert_that(sccp, equal_to(sccp_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        sccp = self.add_sccpline(tenant_uuid=tenant.uuid)

        result = sccp_dao.find(sccp.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(sccp))

        result = sccp_dao.find(sccp.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_sccp(self):
        self.assertRaises(NotFoundError, sccp_dao.get, 42)

    def test_get(self):
        sccp_row = self.add_sccpline()

        sccp = sccp_dao.get(sccp_row.id)

        assert_that(sccp, equal_to(sccp_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        sccp_row = self.add_sccpline(tenant_uuid=tenant.uuid)
        sccp = sccp_dao.get(sccp_row.id, tenant_uuids=[tenant.uuid])
        assert_that(sccp, equal_to(sccp_row))

        sccp_row = self.add_sccpline()
        self.assertRaises(
            NotFoundError,
            sccp_dao.get, sccp_row.id, tenant_uuids=[tenant.uuid],
        )


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = sccp_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_search(self):
        sccp = self.add_sccpline()
        expected = SearchResult(1, [sccp])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        sccp1 = self.add_sccpline()
        sccp2 = self.add_sccpline(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [sccp1, sccp2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [sccp2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestCreate(DAOTestCase):

    def test_create_minimal_parameters(self):
        sccp = sccp_dao.create(SCCP(tenant_uuid=self.default_tenant.uuid))

        assert_that(inspect(sccp).persistent)
        assert_that(sccp, has_properties(
            id=not_none(),
            options=empty(),
            name=not_(empty()),
            context='',
            cid_name='',
            cid_num='',
            allow=none(),
            disallow=none(),
        ))

    def test_create_all_parameters(self):
        options = [
            ["cid_name", "Jôhn Smith"],
            ["cid_num", "5551234567"],
            ["disallow", "all"],
            ["allow", "gsm,ulaw"],
        ]

        sccp = SCCP(options=options, tenant_uuid=self.default_tenant.uuid)

        sccp = sccp_dao.create(sccp)

        assert_that(inspect(sccp).persistent)
        assert_that(sccp, has_properties(
            id=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            options=has_items(*options),
            cid_name='Jôhn Smith',
            cid_num='5551234567',
            allow='gsm,ulaw',
            disallow='all',
        ))

    def test_given_option_does_not_exist_then_raises_error(self):
        self.assertRaises(InputError, SCCP, options=[["invalid", "invalid"]])


class TestEdit(DAOTestCase):

    def test_given_allow_and_disallow_are_set_when_removed_then_database_updated(self):
        sccp = self.add_sccpline(
            context='',
            name='',
            cid_name='',
            cid_num='',
            allow="gsm,g729",
            disallow="alaw,ulaw",
        )

        self.session.expire_all()
        sccp.options = []
        sccp_dao.edit(sccp)

        self.session.expire_all()
        assert_that(sccp, has_properties(
            allow=none(),
            disallow=none(),
        ))

    def test_given_allow_and_disallow_are_when_altered_then_database_updated(self):
        sccp = self.add_sccpline(
            context='',
            name='',
            cid_name='',
            cid_num='',
            allow="gsm,g729",
            disallow="alaw,ulaw",
        )

        self.session.expire_all()
        sccp.options = [
            ["allow", "speex"],
            ["disallow", "opus"]
        ]
        sccp_dao.edit(sccp)

        self.session.expire_all()
        assert_that(sccp, has_properties(
            allow='speex',
            disallow='opus',
        ))

    def test_given_cid_name_and_num_set_when_removed_then_cid_name_and_num_not_deleted(self):
        sccp = self.add_sccpline(
            context='',
            name='',
            cid_name='Jôhn Smith',
            cid_num='5551234567',
        )

        self.session.expire_all()
        sccp.options = []
        sccp_dao.edit(sccp)

        self.session.expire_all()
        assert_that(sccp, has_properties(
            cid_name="Jôhn Smith",
            cid_num="5551234567",
        ))

    def test_given_cid_name_and_num_set_when_altered_then_cid_name_and_num_updated(self):
        sccp = self.add_sccpline(
            context='',
            name='',
            cid_name='Jôhn Smith',
            cid_num='5551234567',
        )

        self.session.expire_all()
        sccp.options = [
            ["cid_name", "Roger Wilkins"],
            ["cid_num", "4181234567"]
        ]
        sccp_dao.edit(sccp)

        self.session.expire_all()
        assert_that(sccp, has_properties(
            cid_name="Roger Wilkins",
            cid_num="4181234567",
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        sccp = self.add_sccpline(context='', name='')

        sccp_dao.delete(sccp)

        assert_that(inspect(sccp).deleted)

    def test_given_line_associated_to_sccp_when_deleted_then_line_dissociated(self):
        sccp = self.add_sccpline(context='default', name='1000')
        line = self.add_line(
            context='default',
            name='1000',
            number='1000',
            endpoint_sccp_id=sccp.id,
        )

        sccp_dao.delete(sccp)

        assert_that(line, has_properties(endpoint_sccp_id=none()))


class TestRelations(DAOTestCase):

    # TODO this test should be in linefeatures
    def test_line_relationship(self):
        sccp = self.add_sccpline()
        line = self.add_line(endpoint_sccp_id=sccp.id)

        self.session.flush()

        self.session.expire_all()
        assert_that(sccp.line, equal_to(line))
