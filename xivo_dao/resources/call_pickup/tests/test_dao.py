# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_items,
    has_properties,
    has_property,
    none,
)

from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.helpers.exception import NotFoundError, InputError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as call_pickup_dao


class TestFind(DAOTestCase):

    def test_find_no_call_pickup(self):
        result = call_pickup_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        call_pickup = self.add_pickup()

        result = call_pickup_dao.find(call_pickup.id)

        assert_that(result, equal_to(call_pickup))


class TestGet(DAOTestCase):

    def test_get_no_call_pickup(self):
        self.assertRaises(NotFoundError, call_pickup_dao.get, 42)

    def test_get(self):
        call_pickup = self.add_pickup()

        result = call_pickup_dao.get(call_pickup.id)

        assert_that(result, equal_to(call_pickup))


class TestFindBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_pickup_dao.find_by, invalid=42)

    def test_find_by_name(self):
        call_pickup_row = self.add_pickup(name='Jôhn')

        call_pickup = call_pickup_dao.find_by(name='Jôhn')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.name, equal_to('Jôhn'))

    def test_find_by_description(self):
        call_pickup_row = self.add_pickup(description='found')

        call_pickup = call_pickup_dao.find_by(description='found')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.description, equal_to('found'))

    def test_find_by_enabled(self):
        call_pickup_row = self.add_pickup(enabled=False)

        call_pickup = call_pickup_dao.find_by(enabled=False)

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.enabled, equal_to(False))

    def test_given_call_pickup_does_not_exist_then_returns_null(self):
        call_pickup = call_pickup_dao.find_by(name='42')

        assert_that(call_pickup, none())


class TestGetBy(DAOTestCase):

    def test_given_column_does_not_exist_then_error_raised(self):
        self.assertRaises(InputError, call_pickup_dao.get_by, invalid=42)

    def test_get_by_name(self):
        call_pickup_row = self.add_pickup(name='Jôhn')

        call_pickup = call_pickup_dao.get_by(name='Jôhn')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.name, equal_to('Jôhn'))

    def test_get_by_description(self):
        call_pickup_row = self.add_pickup(description='found')

        call_pickup = call_pickup_dao.get_by(description='found')

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.description, equal_to('found'))

    def test_get_by_enabled(self):
        call_pickup_row = self.add_pickup(enabled=False)

        call_pickup = call_pickup_dao.get_by(enabled=False)

        assert_that(call_pickup.id, equal_to(call_pickup_row.id))
        assert_that(call_pickup.enabled, equal_to(False))

    def test_given_call_pickup_does_not_exist_then_raises_error(self):
        self.assertRaises(NotFoundError, call_pickup_dao.get_by, name='42')


class TestFindAllBy(DAOTestCase):

    def test_find_all_by_no_call_pickups(self):
        result = call_pickup_dao.find_all_by(name='toto')

        assert_that(result, contains())

    def test_find_all_by_renamed_column(self):
        call_pickup1 = self.add_pickup(name='bob', enabled=True)
        call_pickup2 = self.add_pickup(name='alice', enabled=True)

        call_pickups = call_pickup_dao.find_all_by(enabled=True)

        assert_that(call_pickups, has_items(has_property('id', call_pickup1.id),
                                            has_property('id', call_pickup2.id)))

    def test_find_all_by_native_column(self):
        call_pickup1 = self.add_pickup(name='bob', description='description')
        call_pickup2 = self.add_pickup(name='alice', description='description')

        call_pickups = call_pickup_dao.find_all_by(description='description')

        assert_that(call_pickups, has_items(has_property('id', call_pickup1.id),
                                            has_property('id', call_pickup2.id)))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = call_pickup_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_call_pickups_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_commented_call_pickup_then_returns_one_result(self):
        call_pickup = self.add_pickup(name='bob')
        expected = SearchResult(1, [call_pickup])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleCallPickups(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.call_pickup1 = self.add_pickup(
            name='Ashton',
            description='resto',
        )
        self.call_pickup2 = self.add_pickup(name='Beaugarton', description='bar')
        self.call_pickup3 = self.add_pickup(name='Casa', description='resto')
        self.call_pickup4 = self.add_pickup(name='Dunkin', description='resto')

    def test_when_searching_then_returns_one_result(self):
        expected = SearchResult(1, [self.call_pickup2])

        self.assert_search_returns_result(expected, search='eau')

    def test_when_searching_with_an_extra_argument(self):
        expected_resto = SearchResult(1, [self.call_pickup1])
        self.assert_search_returns_result(expected_resto, search='ton', description='resto')

        expected_bar = SearchResult(1, [self.call_pickup2])
        self.assert_search_returns_result(expected_bar, search='ton', description='bar')

        expected_all_resto = SearchResult(3, [self.call_pickup1, self.call_pickup3, self.call_pickup4])
        self.assert_search_returns_result(expected_all_resto, description='resto', order='name')

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.call_pickup1,
                                    self.call_pickup2,
                                    self.call_pickup3,
                                    self.call_pickup4])

        self.assert_search_returns_result(expected, order='name')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.call_pickup4,
                                    self.call_pickup3,
                                    self.call_pickup2,
                                    self.call_pickup1])

        self.assert_search_returns_result(expected, order='name', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_pickup1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.call_pickup2, self.call_pickup3, self.call_pickup4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(3, [self.call_pickup2])

        self.assert_search_returns_result(expected,
                                          search='a',
                                          order='name',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def setUp(self):
        super(TestCreate, self).setUp()
        self.tenant = self.add_tenant()
        self.entity = self.add_entity()

    def test_create_minimal_fields(self):
        call_pickup = CallPickup(name='name')

        result = call_pickup_dao.create(call_pickup)

        row = self.session.query(CallPickup).first()
        assert_that(result, equal_to(row))
        assert_that(result, has_properties(
            name='name',
            description=none(),
            enabled=True,
        ))

    def test_create_with_all_fields(self):
        call_pickup = CallPickup(
            name='name',
            description='description',
            enabled=False,
        )

        result = call_pickup_dao.create(call_pickup)

        row = self.session.query(CallPickup).first()
        assert_that(result, equal_to(row))
        assert_that(result, has_properties(
            name='name',
            description='description',
            enabled=False,
        ))

    def test_create_fill_default_values(self):
        call_pickup1 = CallPickup(name='name1')
        call_pickup2 = CallPickup(name='name2')

        result1 = call_pickup_dao.create(call_pickup1)
        result2 = call_pickup_dao.create(call_pickup2)

        assert_that(result1, has_properties(
            entity_id=self.entity.id,
            id=1,
        ))
        assert_that(result2, has_properties(
            entity_id=self.entity.id,
            id=2,
        ))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        call_pickup = self.add_pickup(
            name='name',
            description='description',
            enabled=True,
        )

        call_pickup = call_pickup_dao.get(call_pickup.id)
        call_pickup.name = 'other_name'
        call_pickup.description = 'other_description'
        call_pickup.enabled = False

        call_pickup_dao.edit(call_pickup)

        row = self.session.query(CallPickup).first()
        assert_that(row, has_properties(
            name='other_name',
            description='other_description',
            enabled=False,
        ))


class TestDelete(DAOTestCase):

    def test_delete(self):
        call_pickup = self.add_pickup()

        call_pickup_dao.delete(call_pickup)

        row = self.session.query(CallPickup).first()
        assert_that(row, none())
