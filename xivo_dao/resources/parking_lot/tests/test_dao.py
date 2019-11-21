# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as parking_lot_dao


class TestFind(DAOTestCase):

    def test_find_no_parking_lot(self):
        result = parking_lot_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        parking_lot_row = self.add_parking_lot()

        parking_lot = parking_lot_dao.find(parking_lot_row.id)

        assert_that(parking_lot, equal_to(parking_lot_row))

    def test_find_multi_tenant(self):
        tenant = self.add_tenant()
        parking_lot = self.add_parking_lot(tenant_uuid=tenant.uuid)

        result = parking_lot_dao.find(parking_lot.id, tenant_uuids=[tenant.uuid])
        assert_that(result, equal_to(parking_lot))

        result = parking_lot_dao.find(parking_lot.id, tenant_uuids=[self.default_tenant.uuid])
        assert_that(result, none())


class TestGet(DAOTestCase):

    def test_get_no_parking_lot(self):
        self.assertRaises(NotFoundError, parking_lot_dao.get, 42)

    def test_get(self):
        parking_lot_row = self.add_parking_lot()

        parking_lot = parking_lot_dao.get(parking_lot_row.id)

        assert_that(parking_lot.id, equal_to(parking_lot.id))

    def test_get_multi_tenant(self):
        tenant = self.add_tenant()

        parking_lot_row = self.add_parking_lot(tenant_uuid=tenant.uuid)
        parking_lot = parking_lot_dao.get(parking_lot_row.id, tenant_uuids=[tenant.uuid])
        assert_that(parking_lot, equal_to(parking_lot_row))

        parking_lot_row = self.add_parking_lot()
        self.assertRaises(
            NotFoundError,
            parking_lot_dao.get, parking_lot_row.id, tenant_uuids=[tenant.uuid],
        )


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, parking_lot_dao.find_by, invalid=42)

    def test_find_by_name(self):
        parking_lot_row = self.add_parking_lot(name='Jôhn')

        parking_lot = parking_lot_dao.find_by(name='Jôhn')

        assert_that(parking_lot, equal_to(parking_lot_row))
        assert_that(parking_lot.name, equal_to('Jôhn'))

    def test_given_parking_lot_does_not_exist_then_returns_null(self):
        parking_lot = parking_lot_dao.find_by(name='42')

        assert_that(parking_lot, none())

    def test_find_by_multi_tenant(self):
        tenant = self.add_tenant()

        parking_lot_row = self.add_parking_lot()
        parking_lot = parking_lot_dao.find_by(id=parking_lot_row.id, tenant_uuids=[tenant.uuid])
        assert_that(parking_lot, none())

        parking_lot_row = self.add_parking_lot(tenant_uuid=tenant.uuid)
        parking_lot = parking_lot_dao.find_by(id=parking_lot_row.id, tenant_uuids=[tenant.uuid])
        assert_that(parking_lot, equal_to(parking_lot_row))


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, parking_lot_dao.get_by, invalid=42)

    def test_get_by_name(self):
        parking_lot_row = self.add_parking_lot(name='Jôhn')

        parking_lot = parking_lot_dao.get_by(name='Jôhn')

        assert_that(parking_lot, equal_to(parking_lot_row))
        assert_that(parking_lot.name, equal_to('Jôhn'))

    def test_given_parking_lot_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, parking_lot_dao.get_by, name='42')

    def test_get_by_multi_tenant(self):
        tenant = self.add_tenant()

        parking_lot_row = self.add_parking_lot()
        self.assertRaises(
            NotFoundError,
            parking_lot_dao.get_by, id=parking_lot_row.id, tenant_uuids=[tenant.uuid],
        )

        parking_lot_row = self.add_parking_lot(tenant_uuid=tenant.uuid)
        parking_lot = parking_lot_dao.get_by(id=parking_lot_row.id, tenant_uuids=[tenant.uuid])
        assert_that(parking_lot, equal_to(parking_lot_row))


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_parking_lots(self):
        result = parking_lot_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        pass

    def test_find_all_by_native_column(self):
        parking_lot1 = self.add_parking_lot(name='bob', music_on_hold='music_on_hold')
        parking_lot2 = self.add_parking_lot(name='alice', music_on_hold='music_on_hold')

        parking_lots = parking_lot_dao.find_all_by(music_on_hold='music_on_hold')

        assert_that(parking_lots, has_items(
            has_property('id', parking_lot1.id),
            has_property('id', parking_lot2.id),
        ))

    def test_find_all_multi_tenant(self):
        tenant = self.add_tenant()

        parking_lot1 = self.add_parking_lot(name='name', tenant_uuid=tenant.uuid)
        parking_lot2 = self.add_parking_lot(name='name')

        tenants = [tenant.uuid, self.default_tenant.uuid]
        parking_lots = parking_lot_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(parking_lots, has_items(parking_lot1, parking_lot2))

        tenants = [tenant.uuid]
        parking_lots = parking_lot_dao.find_all_by(name='name', tenant_uuids=tenants)
        assert_that(parking_lots, all_of(has_items(parking_lot1), not_(has_items(parking_lot2))))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = parking_lot_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_parking_lots_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_parking_lot_then_returns_one_result(self):
        parking_lot = self.add_parking_lot(name='bob')
        expected = SearchResult(1, [parking_lot])

        self.assert_search_returns_result(expected)

    def test_search_multi_tenant(self):
        tenant = self.add_tenant()

        parking_lot1 = self.add_parking_lot()
        parking_lot2 = self.add_parking_lot(tenant_uuid=tenant.uuid)

        expected = SearchResult(2, [parking_lot1, parking_lot2])
        tenants = [tenant.uuid, self.default_tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)

        expected = SearchResult(1, [parking_lot2])
        tenants = [tenant.uuid]
        self.assert_search_returns_result(expected, tenant_uuids=tenants)


class TestSearchGivenMultipleParkingLots(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.parking_lot1 = self.add_parking_lot(name='Ashton', music_on_hold='resto')
        self.parking_lot2 = self.add_parking_lot(name='Beaugarton', music_on_hold='bar')
        self.parking_lot3 = self.add_parking_lot(name='Casa', music_on_hold='resto')
        self.parking_lot4 = self.add_parking_lot(name='Dunkin', music_on_hold='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.parking_lot2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.parking_lot1])
        self.assert_search_returns_result(expected_resto, search='ton', music_on_hold='resto')

        expected_bar = SearchResult(1, [self.parking_lot2])
        self.assert_search_returns_result(expected_bar, search='ton', music_on_hold='bar')

        expected_all_resto = SearchResult(3, [self.parking_lot1, self.parking_lot3, self.parking_lot4])
        self.assert_search_returns_result(expected_all_resto, music_on_hold='resto', order='name')

    def test_when_searching_with_a_custom_extra_argument(self):
        expected_allow = SearchResult(1, [self.parking_lot2])
        self.assert_search_returns_result(expected_allow, music_on_hold='bar')

        expected_all_deny = SearchResult(3, [self.parking_lot1, self.parking_lot3, self.parking_lot4])
        self.assert_search_returns_result(expected_all_deny, music_on_hold='resto')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [
            self.parking_lot1,
            self.parking_lot2,
            self.parking_lot3,
            self.parking_lot4,
        ])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [
            self.parking_lot4,
            self.parking_lot3,
            self.parking_lot2,
            self.parking_lot1,
        ])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.parking_lot1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_offset_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.parking_lot2, self.parking_lot3, self.parking_lot4])

        self.assert_search_returns_result(expected, offset=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.parking_lot2])

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
        parking_lot_model = ParkingLot(
            tenant_uuid=self.default_tenant.uuid,
            slots_start='701',
            slots_end='750',
        )
        parking_lot = parking_lot_dao.create(parking_lot_model)

        self.session.expire_all()
        assert_that(inspect(parking_lot).persistent)
        assert_that(parking_lot, has_properties(
            id=is_not(none()),
            tenant_uuid=self.default_tenant.uuid,
            name=None,
            slots_start='701',
            slots_end='750',
            timeout=None,
            music_on_hold=None,
        ))

    def test_create_with_all_fields(self):
        parking_lot_model = ParkingLot(
            tenant_uuid=self.default_tenant.uuid,
            name='parking lot',
            slots_start='701',
            slots_end='750',
            timeout=None,
            music_on_hold='music',
        )
        parking_lot = parking_lot_dao.create(parking_lot_model)

        self.session.expire_all()
        assert_that(inspect(parking_lot).persistent)
        assert_that(parking_lot, has_properties(
            tenant_uuid=self.default_tenant.uuid,
            name='parking lot',
            slots_start='701',
            slots_end='750',
            timeout=None,
            music_on_hold='music',
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        parking_lot = self.add_parking_lot(
            name='parking lot',
            slots_start='701',
            slots_end='750',
            timeout=None,
            music_on_hold='music',
        )

        self.session.expire_all()
        parking_lot.name = 'other name'
        parking_lot.slots_start = '801'
        parking_lot.slots_end = '850'
        parking_lot.timeout = 10000
        parking_lot.music_on_hold = 'other_music'

        parking_lot_dao.edit(parking_lot)

        self.session.expire_all()
        assert_that(parking_lot, has_properties(
            name='other name',
            slots_start='801',
            slots_end='850',
            timeout=10000,
            music_on_hold='other_music',
        ))

    def test_edit_set_fields_to_null(self):
        parking_lot = self.add_parking_lot(
            name='parking_lot',
            slots_start='701',
            slots_end='750',
            timeout=5555,
            music_on_hold='music',
        )

        self.session.expire_all()
        parking_lot.name = None
        parking_lot.timeout = None
        parking_lot.music_on_hold = None

        parking_lot_dao.edit(parking_lot)

        self.session.expire_all()
        assert_that(parking_lot, has_properties(
            name=none(),
            timeout=none(),
            music_on_hold=none(),
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        parking_lot = self.add_parking_lot()

        parking_lot_dao.delete(parking_lot)

        assert_that(inspect(parking_lot).deleted)

    def test_when_deleting_then_extension_are_dissociated(self):
        parking_lot = self.add_parking_lot()
        extension = self.add_extension(type='parking', typeval=str(parking_lot.id))

        parking_lot_dao.delete(parking_lot)

        row = self.session.query(Extension).first()
        assert_that(row.id, equal_to(extension.id))
        assert_that(row, has_properties(type='user', typeval='0'))
