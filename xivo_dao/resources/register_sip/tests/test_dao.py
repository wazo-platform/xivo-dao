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

from xivo_dao.alchemy.staticsip import StaticSIP as RegisterSIP
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.tests.test_dao import DAOTestCase

from .. import dao as register_sip_dao


class TestFind(DAOTestCase):

    def test_find_no_register_sip(self):
        result = register_sip_dao.find(42)

        assert_that(result, none())

    def test_find(self):
        register_sip_row = self.add_register_sip()

        register_sip = register_sip_dao.find(register_sip_row.id)

        assert_that(register_sip, equal_to(register_sip_row))


class TestGet(DAOTestCase):

    def test_get_no_register_sip(self):
        self.assertRaises(NotFoundError, register_sip_dao.get, 42)

    def test_get(self):
        register_sip_row = self.add_register_sip()

        register_sip = register_sip_dao.get(register_sip_row.id)

        assert_that(register_sip, equal_to(register_sip_row))


class TestSearch(DAOTestCase):

    def assert_search_returns_result(self, search_result, **parameters):
        result = register_sip_dao.search(**parameters)
        assert_that(result, equal_to(search_result))


class TestSimpleSearch(TestSearch):

    def test_given_no_register_sip_then_returns_no_empty_result(self):
        expected = SearchResult(0, [])

        self.assert_search_returns_result(expected)

    def test_given_one_register_sip_then_returns_one_result(self):
        register_sip = self.add_register_sip()
        expected = SearchResult(1, [register_sip])

        self.assert_search_returns_result(expected)

    def test_given_one_register_sip_with_one_staticsip_then_returns_one_result(self):
        self.add_sip_general_settings()
        register_sip = self.add_register_sip()
        expected = SearchResult(1, [register_sip])

        self.assert_search_returns_result(expected)


class TestSearchGivenMultipleRegisterSIP(TestSearch):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.register_sip1 = self.add_register_sip(id=1)
        self.register_sip2 = self.add_register_sip(id=2)
        self.register_sip3 = self.add_register_sip(id=3)
        self.register_sip4 = self.add_register_sip(id=4)

    def test_when_sorting_then_returns_result_in_ascending_order(self):
        expected = SearchResult(4, [self.register_sip1,
                                    self.register_sip2,
                                    self.register_sip3,
                                    self.register_sip4])

        self.assert_search_returns_result(expected, order='id')

    def test_when_sorting_in_descending_order_then_returns_results_in_descending_order(self):
        expected = SearchResult(4, [self.register_sip4,
                                    self.register_sip3,
                                    self.register_sip2,
                                    self.register_sip1])

        self.assert_search_returns_result(expected, order='id', direction='desc')

    def test_when_limiting_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.register_sip1])

        self.assert_search_returns_result(expected, limit=1)

    def test_when_skipping_then_returns_right_number_of_items(self):
        expected = SearchResult(4, [self.register_sip2, self.register_sip3, self.register_sip4])

        self.assert_search_returns_result(expected, skip=1)

    def test_when_doing_a_paginated_search_then_returns_a_paginated_result(self):
        expected = SearchResult(4, [self.register_sip3])

        self.assert_search_returns_result(expected,
                                          order='id',
                                          direction='desc',
                                          skip=1,
                                          limit=1)


class TestCreate(DAOTestCase):

    def test_create_minimal_fields(self):
        register_sip = RegisterSIP(filename='sip.conf',
                                   category='general',
                                   var_name='register')
        created_register_sip = register_sip_dao.create(register_sip)

        row = self.session.query(RegisterSIP).first()

        assert_that(created_register_sip, equal_to(row))
        assert_that(created_register_sip, has_properties(var_val=none()))

    def test_create_with_all_fields(self):
        register_sip = RegisterSIP(filename='sip.conf',
                                   category='general',
                                   var_name='register',
                                   var_val='valid-chansip-register')

        created_register_sip = register_sip_dao.create(register_sip)

        row = self.session.query(RegisterSIP).first()

        assert_that(created_register_sip, equal_to(row))
        assert_that(created_register_sip, has_properties(var_val='valid-chansip-register'))


class TestEdit(DAOTestCase):

    def test_edit_all_fields(self):
        register_sip = register_sip_dao.create(RegisterSIP(filename='sip.conf',
                                                           category='general',
                                                           var_name='register',
                                                           var_val='valid-chansip-register'))

        register_sip = register_sip_dao.get(register_sip.id)
        register_sip.var_val = 'other-chansip-register'

        register_sip_dao.edit(register_sip)

        row = self.session.query(RegisterSIP).first()

        assert_that(register_sip, equal_to(row))
        assert_that(row, has_properties(var_val='other-chansip-register'))


class TestDelete(DAOTestCase):

    def test_delete(self):
        register_sip = self.add_register_sip()

        register_sip_dao.delete(register_sip)

        row = self.session.query(RegisterSIP).first()
        assert_that(row, none())

    def test_delete_when_associate_with_trunk(self):
        register_sip = self.add_register_sip()
        self.add_trunk(registerid=register_sip.id, registercommented=1, protocol='sip')

        register_sip_dao.delete(register_sip)

        row = self.session.query(RegisterSIP).first()
        assert_that(row, none())

        row = self.session.query(TrunkFeatures).first()
        assert_that(row, has_properties(registerid=0, registercommented=0))

    def test_delete_when_has_trunk_with_same_register_id_and_not_same_protocol(self):
        register_sip = self.add_register_sip()
        register_iax_id = register_sip.id
        self.add_trunk(registerid=register_iax_id, registercommented=1, protocol='iax')

        register_sip_dao.delete(register_sip)

        row = self.session.query(RegisterSIP).first()
        assert_that(row, none())

        row = self.session.query(TrunkFeatures).first()
        assert_that(row, has_properties(registerid=register_iax_id, registercommented=1))
