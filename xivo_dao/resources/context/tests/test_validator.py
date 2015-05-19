# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from xivo_dao.resources.context.model import Context, ContextType
from xivo_dao.resources.context import validator
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import InputError


class TestValidator(unittest.TestCase):

    def test_validate_create_no_parameters(self):
        context = Context()

        self.assertRaises(InputError, validator.validate_create, context)

    def test_validate_create_missing_parameters(self):
        context = Context(display_name='Test')

        self.assertRaises(InputError, validator.validate_create, context)

    def test_validate_create_empty_parameters(self):
        context = Context(name='', display_name='', type='')

        self.assertRaises(InputError, validator.validate_create, context)

    def test_validate_create_invalid_type(self):
        context = Context(name='test', display_name='test', type='invalidtype')

        self.assertRaises(InputError, validator.validate_create, context)

    @patch('xivo_dao.context_dao.get')
    def test_validate_create_context_already_exists(self, context_dao_get):
        context_name = 'test'

        existing_context = Mock(Context)
        existing_context.name = context_name

        context_dao_get.return_value = existing_context

        context = Context(name=context_name,
                          display_name=context_name,
                          type=ContextType.internal)

        self.assertRaises(ResourceError, validator.validate_create, context)

        context_dao_get.assert_called_once_with(context_name)
