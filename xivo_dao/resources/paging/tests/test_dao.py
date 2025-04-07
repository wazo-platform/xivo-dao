# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.paging import Paging
from xivo_dao.helpers.exception import InputError, NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as paging_dao


class TestFind(DAOTestCase):
    def test_find_no_paging(self):
        result = paging_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        paging_row = self.add_paging()

        paging = paging_dao.find(paging_row.id)

        assert_that(paging, equal_to(paging_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        paging = self.add_paging(tenant_uuid=tenant.uuid)

        result = paging_dao.find(paging.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(paging))

        result = paging_dao.find(paging.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):
    def test_get_no_paging(self):
        self.assertRaises(NotFoundError, paging_dao.get, 42)

    def test_get(self):
        paging_row = self.add_paging()

        paging = paging_dao.get(paging_row.id)

        assert_that(paging.id, equal_to(paging.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        paging_row = self.add_paging(tenant_uuid=tenant.uuid)
        paging = paging_dao.get(paging_row.id, tenant_uuids=[tenant.uuid])
        assert_that(paging, equal_to(paging_row))

        paging_row = self.add_paging()
        self.assertRaises(
            NotFoundError,
            paging_dao.get,
            paging_row.id,
            tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, paging_dao.find_by, invalid=42)

    def test_find_by_number(self):
        paging_row = self.add_paging(number='123')

        paging = paging_dao.find_by(number='123')

        assert_that(paging, equal_to(paging_row))
        assert_that(paging.number, equal_to('123'))

    def test_given_paging_does_not_exist_then_returns_null(self):
        paging = paging_dao.find_by(number='42')

        assert_that(paging, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        paging_row = self.add_paging()
        paging = paging_dao.find_by(id=paging_row.id, tenant_uuids=[tenant.uuid])
        assert_that(paging, none())

        paging_row = self.add_paging(tenant_uuid=tenant.uuid)
        paging = paging_dao.find_by(id=paging_row.id, tenant_uuids=[tenant.uuid])
        assert_that(paging, equal_to(paging_row))


class TestGetBy(DAOTestCase):
    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, paging_dao.get_by, invalid=42)

    def test_get_by_number(self):
        paging_row = self.add_paging(number='123')

        paging = paging_dao.get_by(number='123')

        assert_that(paging, equal_to(paging_row))
        assert_that(paging.number, equal_to('123'))

    def test_given_paging_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, paging_dao.get_by, number='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        paging_row = self.add_paging()
        self.assertRaises(
            NotFoundError,
            paging_dao.get_by,
            id=paging_row.id,
            tenant_uuids=[tenant.uuid],
        )

        paging_row = self.add_paging(tenant_uuid=tenant.uuid)
        paging = paging_dao.get_by(id=paging_row.id, tenant_uuids=[tenant.uuid])
        assert_that(paging, equal_to(paging_row))


class TestFindAllBy(DAOTestCase):
    def test_find_all_by_no_pagings(self):
        result = paging_dao.find_all_by(number='123')

        assert_that(result, contains_exactly())

    def test_find_all_by_renamed_column(self):
        paging1 = self.add_paging(announce_sound='sound')
        paging2 = self.add_paging(announce_sound='sound')

        pagings = paging_dao.find_all_by(announce_sound='sound')

        assert_that(
            pagings,
            has_items(
                has_property('id', paging1.id),
                has_property('id', paging2.id),
            ),
        )

    def test_find_all_by_native_column(self):
        paging1 = self.add_paging(name='paging')
        paging2 = self.add_paging(name='paging')

        pagings = paging_dao.find_all_by(name='paging')

        assert_that(
            pagings,
            has_items(
                has_property('id', paging1.id),
                has_property('id', paging2.id),
            ),
        )

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        paging1 = self.add_paging(description='description', tenant_uuid=tenant.uuid)
        paging2 = self.add_paging(description='description')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        pagings = paging_dao.find_all_by(
            description='description', tenant_uuids=tenants
        )
        assert_that(pagings, has_items(paging1, paging2))

        tenants = [tenant.uuid]
        pagings = paging_dao.find_all_by(
            description='description', tenant_uuids=tenants
        )
        assert_that(pagings, all_of(has_items(paging1), not_(has_items(paging2))))


class TestSearch(DAOTestCase):
    def assert_search_returns_result(self, search_result, **parameters):
        result = paging_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):
    def test_given_no_pagings_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_paging_then_returns_one_result(self):
        paging = self.add_paging()
        expected = SearchResult(1, [paging])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        paging1 = self.add_paging()
        paging2 = self.add_paging(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [paging1, paging2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [paging2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultiplePagings(TestSearch):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.paging1 = self.add_paging(name='Ashton', announce_sound='resto')
        self.paging2 = self.add_paging(name='Beaugarton', announce_sound='bar')
        self.paging3 = self.add_paging(name='Casa', announce_sound='resto')
        self.paging4 = self.add_paging(name='Dunkin', announce_sound='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.paging2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.paging1])
        self.assert_search_returns_result(
            expected_resto, search='ton', announce_sound='resto'
        )

        expected_bar = SearchResult(1, [self.paging2])
        self.assert_search_returns_result(
            expected_bar, search='ton', announce_sound='bar'
        )

        expected_all_resto = SearchResult(3, [self.paging1, self.paging3, self.paging4])
        self.assert_search_returns_result(
            expected_all_resto, announce_sound='resto', order='announce_sound'
        )

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.paging2])
        self.assert_search_returns_result(expected_allow, announce_sound='bar')

        expected_all_deny = SearchResult(3, [self.paging1, self.paging3, self.paging4])
        self.assert_search_returns_result(expected_all_deny, announce_sound='resto')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(
            4,
            [
                self.paging1,
                self.paging2,
                self.paging3,
                self.paging4,
            ],
        )

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(
        self,
    ):
        expected = SearchResult(
            4,
            [
                self.paging4,
                self.paging3,
                self.paging2,
                self.paging1,
            ],
        )

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.paging1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_name_of_items(self):
        expected = SearchResult(4, [self.paging2, self.paging3, self.paging4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.paging2])

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
        paging_model = Paging(tenant_uuid=self.default_tenant.uuid)
        paging = paging_dao.create(paging_model)

        self.session.expire_all()
        assert_that(inspect(paging).persistent)
        assert_that(
            paging,
            has_properties(
                id=is_not(none()),
                tenant_uuid=self.default_tenant.uuid,
                name=None,
                number=None,
                duplex_bool=False,
                ignore_forward=False,
                record_bool=False,
                caller_notification=True,
                timeout=30,
                announce_sound=None,
                announce_caller=True,
                enabled=True,
            ),
        )

    def test_create_with_all_fields(self):
        paging_model = Paging(
            tenant_uuid=self.default_tenant.uuid,
            name='paging',
            number='123',
            duplex_bool=True,
            ignore_forward=True,
            record_bool=True,
            caller_notification=False,
            timeout=40,
            announce_sound='sound',
            announce_caller=False,
            enabled=False,
        )
        paging = paging_dao.create(paging_model)

        self.session.expire_all()
        assert_that(inspect(paging).persistent)
        assert_that(
            paging,
            has_properties(
                tenant_uuid=self.default_tenant.uuid,
                name='paging',
                number='123',
                duplex_bool=True,
                ignore_forward=True,
                record_bool=True,
                caller_notification=False,
                timeout=40,
                announce_sound='sound',
                announce_caller=False,
                enabled=False,
            ),
        )


class TestEdit(DAOTestCase):
    def test_edit_all_fields(self):
        paging = self.add_paging(
            name='paging',
            number='123',
            duplex_bool=True,
            ignore_forward=True,
            record_bool=True,
            caller_notification=False,
            timeout=40,
            announce_sound='sound',
            announce_caller=False,
            enabled=False,
        )

        self.session.expire_all()
        paging.name = 'other_paging'
        paging.number = '456'
        paging.duplex_bool = False
        paging.ignore_forward = False
        paging.record_bool = False
        paging.caller_notification = True
        paging.timeout = 50
        paging.announce_sound = 'other_sound'
        paging.announce_caller = True
        paging.enabled = True

        paging_dao.edit(paging)

        self.session.expire_all()
        assert_that(
            paging,
            has_properties(
                name='other_paging',
                number='456',
                duplex_bool=False,
                ignore_forward=False,
                record_bool=False,
                caller_notification=True,
                timeout=50,
                announce_sound='other_sound',
                announce_caller=True,
                enabled=True,
            ),
        )

    def test_edit_set_fields_to_null(self):
        paging = self.add_paging(
            name='paging',
            number='123',
            announce_sound='sound',
        )

        self.session.expire_all()
        paging.name = None
        paging.number = None
        paging.announce_sound = None

        paging_dao.edit(paging)

        self.session.expire_all()
        assert_that(
            paging,
            has_properties(
                name=none(),
                number=none(),
                announce_sound=none(),
            ),
        )


class TestDelete(DAOTestCase):
    def test_delete(self):
        paging = self.add_paging()

        paging_dao.delete(paging)

        assert_that(inspect(paging).deleted)
