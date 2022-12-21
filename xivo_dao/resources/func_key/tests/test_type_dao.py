# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import none

from xivo_dao.resources.func_key import type_dao as dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestFindTypeForName(DAOTestCase):

    def test_given_no_types_then_returns_none(self):
        result = dao.find_type_for_name('type')

        assert_that(result, none())

    def test_given_one_type_when_queried_returns_one_row(self):
        type_name = 'speeddial'
        self.add_func_key_type(name=type_name)

        result = dao.find_type_for_name(type_name)

        assert_that(result, has_property('name', type_name))

    def test_given_one_type_when_other_name_queried_returns_none(self):
        self.add_func_key_type(name='speeddial')

        result = dao.find_type_for_name('transfer')

        assert_that(result, none())

    def test_given_two_types_when_one_queried_returns_right_row(self):
        self.add_func_key_type(name='speeddial')
        self.add_func_key_type(name='transfer')

        result = dao.find_type_for_name('transfer')

        assert_that(result, has_property('name', 'transfer'))


class BaseTestFuncKeyDestinationTypeExists(DAOTestCase):

    def test_given_no_destination_types_then_returns_none(self):
        result = dao.find_destination_type_for_name('type')

        assert_that(result, none())

    def test_given_one_destination_type_when_queried_returns_true(self):
        name = 'user'
        self.add_func_key_destination_type(id=1, name=name)

        result = dao.find_destination_type_for_name(name)

        assert_that(result, has_property('name', name))

    def test_given_one_destination_type_when_other_name_queried_returns_false(self):
        self.add_func_key_destination_type(id=1, name='user')

        result = dao.find_destination_type_for_name('queue')

        assert_that(result, none())

    def test_given_two_destination_types_when_one_queried_returns_true(self):
        self.add_func_key_destination_type(id=1, name='user')
        self.add_func_key_destination_type(id=2, name='queue')

        result = dao.find_destination_type_for_name('queue')

        assert_that(result, has_property('name', 'queue'))
