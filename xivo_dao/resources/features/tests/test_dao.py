# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, none, equal_to

from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.features import dao as feature_dao


class TestFindParkPositionRange(DAOTestCase):

    def test_given_parking_is_disabled_then_returns_nothing(self):
        self.add_features(var_name='parkpos',
                          var_val='701-750',
                          commented=1)

        result = feature_dao.find_park_position_range()

        assert_that(result, none())

    def test_given_parking_is_enabled_then_returns_range(self):
        self.add_features(var_name='parkpos',
                          var_val='701-750')

        expected = (701, 750)

        result = feature_dao.find_park_position_range()

        assert_that(result, equal_to(expected))


class TestGetValue(DAOTestCase):

    def test_when_getting_feature_by_id_then_returns_value(self):
        self.add_features(id=12,
                          var_name='parkext',
                          var_val='700')

        result = feature_dao.get_value(12)

        assert_that(result, equal_to('700'))

    def test_given_no_features_then_raises_error(self):
        self.assertRaises(NotFoundError, feature_dao.get_value, 12)
