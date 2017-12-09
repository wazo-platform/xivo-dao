# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import (
    assert_that,
    equal_to,
    has_properties,
    none,
)

from xivo_dao.alchemy.staticiax import StaticIAX as RegisterIAX
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as register_iax_dao


class TestFind(DAOTestCase):

    def test_find_no_register_iax(self):
        result = register_iax_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        register_iax_row = self.add_register_iax()

        register_iax = register_iax_dao.find(register_iax_row.id)

        assert_that(register_iax, equal_to(register_iax_row))


class TestGet(DAOTestCase):

    def test_get_no_register_iax(self):
        self.assertRaises(NotFoundError, register_iax_dao.get, 42)

    def test_get(self):
        register_iax_row = self.add_register_iax()

        register_iax = register_iax_dao.get(register_iax_row.id)

        assert_that(register_iax, equal_to(register_iax_row))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = register_iax_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_register_iax_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_register_iax_then_returns_one_result(self):
        register_iax = self.add_register_iax()
        expected = SearchResult(1, [register_iax])

        self.assert_search_returns_result(expected)

    def test_given_one_register_iax_with_one_staticiax_then_returns_one_result(self):
        self.add_iax_general_settings()
        register_iax = self.add_register_iax()
        expected = SearchResult(1, [register_iax])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleRegisterIAX(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.register_iax1 = self.add_register_iax(id=1)
        self.register_iax2 = self.add_register_iax(id=2)
        self.register_iax3 = self.add_register_iax(id=3)
        self.register_iax4 = self.add_register_iax(id=4)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.register_iax1,
                                    self.register_iax2,
                                    self.register_iax3,
                                    self.register_iax4])

        self.assert_search_returns_result(expected, order='id')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.register_iax4,
                                    self.register_iax3,
                                    self.register_iax2,
                                    self.register_iax1])

        self.assert_search_returns_result(expected, order='id', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.register_iax1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.register_iax2, self.register_iax3, self.register_iax4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(4, [self.register_iax3])

        self.assert_search_returns_result(expected,
                                          order='id',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        register_iax = RegisterIAX(filename='iax.conf',
                                   category='general',
                                   var_name='register')
        created_register_iax = register_iax_dao.create(register_iax)

        row = self.session.query(RegisterIAX).first()

        assert_that(created_register_iax, equal_to(row))
        assert_that(created_register_iax, has_properties(var_val=none()))

    def test_create_with_all_fields(self):
        register_iax = RegisterIAX(filename='iax.conf',
                                   category='general',
                                   var_name='register',
                                   var_val='valid-chaniax-register')

        created_register_iax = register_iax_dao.create(register_iax)

        row = self.session.query(RegisterIAX).first()

        assert_that(created_register_iax, equal_to(row))
        assert_that(created_register_iax, has_properties(var_val='valid-chaniax-register'))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        register_iax = register_iax_dao.create(RegisterIAX(filename='iax.conf',
                                                           category='general',
                                                           var_name='register',
                                                           var_val='valid-chaniax-register'))

        register_iax = register_iax_dao.get(register_iax.id)
        register_iax.var_val = 'other-chaniax-register'

        register_iax_dao.edit(register_iax)

        row = self.session.query(RegisterIAX).first()

        assert_that(register_iax, equal_to(row))
        assert_that(row, has_properties(var_val='other-chaniax-register'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        register_iax = self.add_register_iax()

        register_iax_dao.delete(register_iax)

        row = self.session.query(RegisterIAX).first()
        assert_that(row, none())

    def test_delete_when_associate_with_trunk(self):
        register_iax = self.add_register_iax()
        self.add_trunk(registerid=register_iax.id, registercommented=1, protocol='iax')

        register_iax_dao.delete(register_iax)

        row = self.session.query(RegisterIAX).first()
        assert_that(row, none())

        row = self.session.query(TrunkFeatures).first()
        assert_that(row, has_properties(registerid=0, registercommented=0))

    def test_delete_when_has_trunk_with_same_register_id_and_not_same_protocol(self):
        register_iax = self.add_register_iax()
        register_iax_id = register_iax.id
        self.add_trunk(registerid=register_iax_id, registercommented=1, protocol='sip')

        register_iax_dao.delete(register_iax)

        row = self.session.query(RegisterIAX).first()
        assert_that(row, none())

        row = self.session.query(TrunkFeatures).first()
        assert_that(row, has_properties(registerid=register_iax_id, registercommented=1))
