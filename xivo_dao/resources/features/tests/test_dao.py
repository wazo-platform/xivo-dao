# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, contains, has_items, none, equal_to

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
