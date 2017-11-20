# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, contains, has_items, none, equal_to

from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.features.model import TransferExtension
from xivo_dao.resources.features import dao as feature_dao


class TestFindAllTransferExtensions(DAOTestCase):

    def prepare_features(self):
        transfers = []

        row = self.add_features(category='featuremap',
                                var_name='blindxfer',
                                var_val='*1')
        model = TransferExtension(id=row.id,
                                  exten='*1',
                                  transfer='blind')
        transfers.append(model)

        row = self.add_features(category='featuremap',
                                var_name='atxfer',
                                var_val='*2')
        model = TransferExtension(id=row.id,
                                  exten='*2',
                                  transfer='attended')
        transfers.append(model)

        return transfers

    def test_given_no_features_then_return_empty_list(self):
        extensions = feature_dao.find_all_transfer_extensions()

        assert_that(extensions, contains())

    def test_given_all_transfer_features_then_returns_models(self):
        expected = self.prepare_features()

        result = feature_dao.find_all_transfer_extensions()

        assert_that(result, has_items(*expected))

    def test_given_feature_is_commented_then_returns_empty_list(self):
        self.add_features(category='featuremap',
                          var_name='blindxfer',
                          var_val='*1',
                          commented=1)

        result = feature_dao.find_all_transfer_extensions()

        assert_that(result, contains())


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
