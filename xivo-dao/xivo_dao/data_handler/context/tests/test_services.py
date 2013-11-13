# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock, patch
from hamcrest import all_of, assert_that, equal_to, has_property

from xivo_dao.data_handler.context import services as context_services
from xivo_dao.data_handler.context.services import ContextRange

from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.exception import InvalidParametersError


class TestContext(unittest.TestCase):

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name_inexistant(self, context_dao_get):
        context_name = 'inexistant_context'
        context_dao_get.return_value = None

        result = context_services.find_by_name(context_name)

        assert_that(result, equal_to(None))

    @patch('xivo_dao.context_dao.get')
    def test_find_by_name(self, context_dao_get):
        context_name = 'my_context'
        context_mock = Mock()
        context_dao_get.return_value = context_mock

        result = context_services.find_by_name(context_name)

        assert_that(result, equal_to(context_mock))

    @patch('xivo_dao.data_handler.context.validator.validate_create')
    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create(self, context_dao_create, validate_create):
        context_name = 'test'

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        context_dao_create.return_value = context

        result = context_services.create(context)

        validate_create.assert_called_once_with(context)
        context_dao_create.assert_called_once_with(context)

        assert_that(result, all_of(
            has_property('name', context_name),
            has_property('display_name', context_name),
            has_property('type', ContextType.internal)))

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    @patch('xivo_dao.data_handler.context.services.is_extension_included_in_ranges')
    def test_is_extension_valid_for_context(self, is_extension_included_in_ranges, find_all_context_ranges):
        extension = Mock(Extension, exten='1000', context='default')

        context_ranges = find_all_context_ranges.return_value = Mock()
        is_extension_included_in_ranges.return_value = True

        result = context_services.is_extension_valid_for_context(extension)

        assert_that(result, equal_to(True))
        find_all_context_ranges.assert_called_once_with(extension.context)
        is_extension_included_in_ranges.assert_called_once_with(1000, context_ranges)

    def test_is_extension_included_in_ranges_when_no_ranges(self):
        expected = False

        exten = 1000
        context_ranges = []

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_below_minimum(self):
        expected = False

        exten = 1000
        context_ranges = [(2000, 3000)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_above_maximum(self):
        expected = False

        exten = 9999
        context_ranges = [(2000, 3000)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_inside_of_range_lower_limit(self):
        expected = True

        exten = 1000
        context_ranges = [(1000, 3000)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_inside_of_range_upper_limit(self):
        expected = True

        exten = 3000
        context_ranges = [(1000, 3000)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_inside_second_range(self):
        expected = True

        exten = 2000
        context_ranges = [(1000, 1999),
                          (2000, 2999)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_when_ranges_overlap(self):
        expected = True

        exten = 1450
        context_ranges = [(1400, 2000),
                          (1000, 1500)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_with_single_value_using_lesser_value(self):
        expected = False

        exten = 500
        context_ranges = [(1000, None)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_with_single_value_using_greater_value(self):
        expected = False

        exten = 1450
        context_ranges = [(1000, None)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_with_single_value_using_right_value(self):
        expected = True

        exten = 1000
        context_ranges = [(1000, None)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_with_single_value_and_range_when_extension_in_range(self):
        expected = True

        exten = 2000
        context_ranges = [(1000, None),
                          (2000, 3000)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_is_extension_included_in_ranges_with_single_value_and_range_when_extension_on_value(self):
        expected = True

        exten = 1000
        context_ranges = [(2000, 3000),
                          (1000, None)]

        result = context_services.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_valid_for_context_when_extension_is_alphanumeric(self, context_ranges):
        extension = Extension(exten='ABC123',
                              context='default')

        self.assertRaises(InvalidParametersError, context_services.is_extension_valid_for_context, extension)

    @patch('xivo_dao.data_handler.context.dao.find_all_specific_context_ranges')
    @patch('xivo_dao.data_handler.context.services.is_extension_included_in_ranges')
    def test_is_extension_valid_for_context_range(self,
                                                  is_extension_included_in_ranges,
                                                  find_all_specific_context_ranges):
        extension = Extension(exten='1000',
                              context='default')

        context_range = find_all_specific_context_ranges.return_value = Mock()
        is_extension_included_in_ranges.return_value = True

        result = context_services.is_extension_valid_for_context_range(extension, ContextRange.users)

        find_all_specific_context_ranges.assert_called_once_with(extension.context, ContextRange.users)
        is_extension_included_in_ranges.assert_called_once_with(1000, context_range)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.data_handler.context.dao.find_all_context_ranges')
    def test_is_extension_valid_for_context_range_when_extension_is_alphanumeric(self, context_ranges):
        extension = Extension(exten='ABC123',
                              context='default')

        self.assertRaises(InvalidParametersError,
                          context_services.is_extension_valid_for_context_range,
                          extension,
                          ContextRange.users)
