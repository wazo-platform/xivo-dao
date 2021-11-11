# -*- coding: utf-8 -*-
# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
    not_,
    not_none,
)
from sqlalchemy.inspection import inspect

from xivo_dao.alchemy.moh import MOH
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as moh_dao

UUID = 'abc-123-4567'


class TestFind(DAOTestCase):

    def test_find_no_moh(self):
        result = moh_dao.find(UUID)

        assert_that(result, none())

    def test_find(self):
        moh_row = self.add_moh()

        moh = moh_dao.find(moh_row.uuid)

        assert_that(moh, equal_to(moh_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        moh = self.add_moh(tenant_uuid=tenant.uuid)

        result = moh_dao.find(moh.uuid, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(moh))

        result = moh_dao.find(moh.uuid, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_moh(self):
        self.assertRaises(NotFoundError, moh_dao.get, UUID)

    def test_get(self):
        moh_row = self.add_moh()

        moh = moh_dao.get(moh_row.uuid)

        assert_that(moh, equal_to(moh_row))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        moh_row = self.add_moh(tenant_uuid=tenant.uuid)
        moh = moh_dao.get(moh_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(moh, equal_to(moh_row))

        moh_row = self.add_moh()
        self.assertRaises(
            NotFoundError,
            moh_dao.get, moh_row.uuid, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, moh_dao.find_by, invalid=42)

    def test_find_by_name(self):
        moh_row = self.add_moh(name='myname')

        moh = moh_dao.find_by(name='myname')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.name, equal_to('myname'))

    def test_find_by_label(self):
        moh_row = self.add_moh(label='mylabel')

        moh = moh_dao.find_by(label='mylabel')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.label, equal_to('mylabel'))

    def test_given_moh_does_not_exist_then_returns_null(self):
        moh = moh_dao.find_by(uuid=UUID)

        assert_that(moh, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        moh_row = self.add_moh()
        moh = moh_dao.find_by(uuid=moh_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(moh, none())

        moh_row = self.add_moh(tenant_uuid=tenant.uuid)
        moh = moh_dao.find_by(uuid=moh_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(moh, equal_to(moh_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, moh_dao.get_by, invalid=42)

    def test_get_by_name(self):
        moh_row = self.add_moh(name='myname')

        moh = moh_dao.get_by(name='myname')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.name, equal_to('myname'))

    def test_get_by_label(self):
        moh_row = self.add_moh(label='mylabel')

        moh = moh_dao.get_by(label='mylabel')

        assert_that(moh, equal_to(moh_row))
        assert_that(moh.label, equal_to('mylabel'))

    def test_given_moh_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, moh_dao.get_by, uuid=UUID)

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        moh_row = self.add_moh()
        self.assertRaises(
            NotFoundError,
            moh_dao.get_by, uuid=moh_row.uuid, tenant_uuids=[tenant.uuid],
        )

        moh_row = self.add_moh(tenant_uuid=tenant.uuid)
        moh = moh_dao.get_by(uuid=moh_row.uuid, tenant_uuids=[tenant.uuid])
        assert_that(moh, equal_to(moh_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_moh(self):
        result = moh_dao.find_all_by(label='toto')

        assert_that(result, contains())

    def test_find_all_by_native_column(self):
        moh1 = self.add_moh(label='mymoh')
        moh2 = self.add_moh(label='mymoh')

        mohs = moh_dao.find_all_by(label='mymoh')

        assert_that(mohs, has_items(
            has_property('uuid', moh1.uuid),
            has_property('uuid', moh2.uuid),
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        moh1 = self.add_moh(label='label', tenant_uuid=tenant.uuid)
        moh2 = self.add_moh(label='label')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        mohs = moh_dao.find_all_by(label='label', tenant_uuids=tenants)
        assert_that(mohs, has_items(moh1, moh2))

        tenants = [tenant.uuid]
        mohs = moh_dao.find_all_by(label='label', tenant_uuids=tenants)
        assert_that(mohs, all_of(has_items(moh1), not_(has_items(moh2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = moh_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_moh_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_moh_then_returns_one_result(self):
        moh = self.add_moh()
        expected = SearchResult(1, [moh])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        moh1 = self.add_moh(label='moh1')
        moh2 = self.add_moh(label='moh2', tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [moh1, moh2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [moh2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleMOH(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.moh1 = self.add_moh(label='Ashton', name='resto1')
        self.moh2 = self.add_moh(label='Beaugarton', name='bar2')
        self.moh3 = self.add_moh(label='Casa', name='resto3')
        self.moh4 = self.add_moh(label='Dunkin', name='resto4')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.moh2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.moh1])
        self.assert_search_returns_result(expected_resto, search='ton', name='resto1')

        expected_bar = SearchResult(1, [self.moh2])
        self.assert_search_returns_result(expected_bar, search='ton', name='bar2')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.moh1,
            self.moh2,
            self.moh3,
            self.moh4,
        ])

        self.assert_search_returns_result(expected, order='label')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.moh4,
            self.moh3,
            self.moh2,
            self.moh1,
        ])

        self.assert_search_returns_result(expected, order='label', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.moh1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.moh2, self.moh3, self.moh4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.moh3])

        self.assert_search_returns_result(
            expected,
            search='resto',
            order='label',
            direction='desc',
            offset=1,
            limit=1,
        )


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        moh_model = MOH(
            tenant_uuid=self.default_tenant.uuid, name='mymoh', label='mymoh', mode='files',
        )
        moh = moh_dao.create(moh_model)

        self.session.expire_all()
        assert_that(inspect(moh).persistent)
        assert_that(moh, has_properties(
            uuid=not_none(),
            name='mymoh',
            label='mymoh',
            mode='files',
            application=none(),
            sort=none(),
        ))

    def test_create_with_all_fields(self):
        moh_model = MOH(
            tenant_uuid=self.default_tenant.uuid,
            name='mymoh',
            label='moh, you\'re mine',
            mode='files',
            application='/bin/false unused',
            sort='random',
        )

        moh = moh_dao.create(moh_model)

        self.session.expire_all()
        assert_that(inspect(moh).persistent)
        assert_that(moh, has_properties(
            uuid=not_none(),
            tenant_uuid=self.default_tenant.uuid,
            name='mymoh',
            label='moh, you\'re mine',
            mode='files',
            application='/bin/false unused',
            sort='random',
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        moh = self.add_moh(
            name='mymoh',
            label='moh, you\'re mine',
            mode='files',
            application='/bin/false unused',
            sort='random',
        )

        self.session.expire_all()
        moh.name = 'zmymoh'
        moh.label = 'lol'
        moh.mode = 'custom'
        moh.application = '/bin/true'
        moh.sort = 'alpha'

        moh_dao.edit(moh)

        self.session.expire_all()
        assert_that(moh, has_properties(
            uuid=not_none(),
            name='zmymoh',
            label='lol',
            mode='custom',
            application='/bin/true',
            sort='alpha',
        ))

    def test_edit_set_fields_to_null(self):
        moh = self.add_moh(
            name='mymoh',
            label='moh, you\'re mine',
            mode='files',
            application='/bin/false unused',
            sort='random',
        )

        self.session.expire_all()
        moh.application = None
        moh.sort = None

        moh_dao.edit(moh)

        self.session.expire_all()
        assert_that(moh, has_properties(
            uuid=not_none(),
            name='mymoh',
            label='moh, you\'re mine',
            mode='files',
            application=none(),
            sort=none(),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        moh = self.add_moh()

        moh_dao.delete(moh)

        assert_that(inspect(moh).deleted)
