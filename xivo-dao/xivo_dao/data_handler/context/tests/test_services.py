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

from xivo_dao.data_handler.context import services as context_services
from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.exception import MissingParametersError, InvalidParametersError, \
    ElementAlreadyExistsError


from hamcrest import *


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

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_no_parameters(self, context_dao_create):
        context = Context()

        self.assertRaises(MissingParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_missing_parameters(self, context_dao_create):
        context = Context(display_name='Test')

        self.assertRaises(MissingParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_empty_parameters(self, context_dao_create):
        context = Context(name='', display_name='', type='')

        self.assertRaises(InvalidParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_invalid_type(self, context_dao_create):
        context = Context(name='test', display_name='test', type='invalidtype')

        self.assertRaises(InvalidParametersError, context_services.create, context)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create_context_already_exists(self, context_dao_create, find_by_name):
        context_name = 'test'

        existing_context = Mock(Context)
        existing_context.name = context_name

        find_by_name.return_value = existing_context

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        self.assertRaises(ElementAlreadyExistsError, context_services.create, context)

        find_by_name.assert_called_once_with(context_name)
        assert_that(context_dao_create.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.context.dao.create')
    def test_create(self, context_dao_create, find_by_name):
        context_name = 'test'

        find_by_name.return_value = None

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        context_dao_create.return_value = context

        result = context_services.create(context)

        find_by_name.assert_called_once_with(context_name)
        context_dao_create.assert_called_once_with(context)

        assert_that(result, all_of(
            has_property('name', context_name),
            has_property('display_name', context_name),
            has_property('type', ContextType.internal)))
