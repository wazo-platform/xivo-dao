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

from mock import patch, Mock
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.context.model import Context
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementCreationError, ElementAlreadyExistsError, \
    NonexistentParametersError


class TestExtension(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.find_all')
    def test_find_all(self, find_all_dao):
        expected = [Extension()]

        find_all_dao.return_value = expected

        result = extension_services.find_all()

        find_all_dao.assert_called_once_with(order=None, commented=False)
        self.assertEquals(result, expected)

    @patch('xivo_dao.data_handler.extension.dao.find_all')
    def test_find_all_with_commented(self, find_all_dao):
        expected = [Extension()]

        find_all_dao.return_value = expected

        result = extension_services.find_all(commented=True)

        find_all_dao.assert_called_once_with(order=None, commented=True)
        self.assertEquals(result, expected)

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    def test_find_by_exten_context(self, find_by_exten_context):
        expected = Extension(exten='1000', context='default')

        find_by_exten_context.return_value = expected

        result = extension_services.find_by_exten_context(expected.exten, expected.context)

        find_by_exten_context.assert_called_once_with(expected.exten, expected.context)
        self.assertEquals(result, expected)

    def test_create_no_properties(self):
        extension = Extension(exten='1234')

        self.assertRaises(MissingParametersError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_empty_exten(self, extension_dao_create, extension_notifier_created):
        exten = ''
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(InvalidParametersError, extension_services.create, extension)
        self.assertEquals(extension_notifier_created.call_count, 0)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_empty_context(self, extension_dao_create, extension_notifier_created):
        exten = '1324'
        context = ''

        extension = Extension(exten=exten,
                              context=context)

        self.assertRaises(InvalidParametersError, extension_services.create, extension)
        self.assertEquals(extension_notifier_created.call_count, 0)

    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.context.services.find_by_name', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context', Mock(return_value=None))
    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create(self, extension_dao_create, extension_notifier_created):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        extension_dao_create.return_value = extension

        result = extension_services.create(extension)

        extension_dao_create.assert_called_once_with(extension)
        self.assertEquals(type(result), Extension)
        extension_notifier_created.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.context.services.find_by_name', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_when_extension_already_exists(self, extension_dao_create, extension_notifier_created, find_by_exten_context):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        find_by_exten_context.return_value = extension

        self.assertRaises(ElementAlreadyExistsError, extension_services.create, extension)
        self.assertEquals(extension_dao_create.call_count, 0)
        self.assertEquals(extension_notifier_created.call_count, 0)

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_when_context_does_not_exist(self,
                                                extension_dao_create,
                                                extension_notifier_created,
                                                find_by_exten_context,
                                                find_context_by_name):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        find_by_exten_context.return_value = None
        find_context_by_name.return_value = None

        self.assertRaises(NonexistentParametersError, extension_services.create, extension)
        self.assertEquals(extension_dao_create.call_count, 0)
        self.assertEquals(extension_notifier_created.call_count, 0)

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context', Mock(return_value=None))
    @patch('xivo_dao.data_handler.context.services.find_by_name')
    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context')
    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_when_exten_outside_of_range(self,
                                                extension_dao_create,
                                                extension_notifier_created,
                                                is_extension_valid_for_context,
                                                find_context_by_name):
        exten = '9999'
        context_name = 'toto'

        context = Context(name=context_name)

        extension = Extension(exten=exten,
                              context=context_name)

        is_extension_valid_for_context.return_value = False
        find_context_by_name.return_value = context

        self.assertRaises(InvalidParametersError, extension_services.create, extension)
        self.assertEquals(extension_dao_create.call_count, 0)
        self.assertEquals(extension_notifier_created.call_count, 0)
        is_extension_valid_for_context.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context', Mock(return_value=True))
    @patch('xivo_dao.data_handler.context.services.find_by_name', Mock(return_value=Mock()))
    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context', Mock(return_value=None))
    @patch('xivo_dao.data_handler.extension.dao.create')
    def test_create_with_error_from_dao(self, extension_dao_create):
        exten = 'extension'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        error = Exception("message")
        extension_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.deleted')
    @patch('xivo_dao.data_handler.extension.dao.delete')
    def test_delete(self, extension_dao_delete, extension_notifier_deleted):
        exten = 'extension'
        context = 'toto'
        extension = Extension(id=1,
                              exten=exten,
                              context=context)

        extension_services.delete(extension)

        extension_dao_delete.assert_called_once_with(extension)
        extension_notifier_deleted.assert_called_once_with(extension)
