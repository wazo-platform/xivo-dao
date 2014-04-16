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
from mock import patch

from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.exception import ElementCreationError


class TestExtension(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.find_all')
    def test_find_all(self, find_all_dao):
        expected = [Extension()]

        find_all_dao.return_value = expected

        result = extension_services.find_all()

        find_all_dao.assert_called_once_with(order=None)
        self.assertEquals(result, expected)

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    def test_find_by_exten_context(self, find_by_exten_context):
        expected = Extension(exten='1000', context='default')

        find_by_exten_context.return_value = expected

        result = extension_services.find_by_exten_context(expected.exten, expected.context)

        find_by_exten_context.assert_called_once_with(expected.exten, expected.context)
        self.assertEquals(result, expected)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    @patch('xivo_dao.data_handler.extension.validator.validate_create')
    def test_create(self, validate_create, extension_dao_create, extension_notifier_created):
        exten = '1000'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        extension_dao_create.return_value = extension

        result = extension_services.create(extension)

        self.assertEquals(type(result), Extension)
        validate_create.assert_called_once_with(extension)
        extension_dao_create.assert_called_once_with(extension)
        extension_notifier_created.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.extension.notifier.created')
    @patch('xivo_dao.data_handler.extension.dao.create')
    @patch('xivo_dao.data_handler.extension.validator.validate_create')
    def test_create_with_error_from_dao(self, validate_create, extension_dao_create, extension_notifier_created):
        exten = '1000'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        error = Exception("message")
        extension_dao_create.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, extension_services.create, extension)

    @patch('xivo_dao.data_handler.extension.notifier.edited')
    @patch('xivo_dao.data_handler.extension.dao.edit')
    @patch('xivo_dao.data_handler.extension.validator.validate_edit')
    def test_edit(self, validate_edit, extension_dao_edit, extension_notifier_edited):
        exten = '1000'
        context = 'toto'

        extension = Extension(id=1,
                              exten=exten,
                              context=context)

        extension_dao_edit.return_value = extension

        extension_services.edit(extension)

        validate_edit.assert_called_once_with(extension)
        extension_dao_edit.assert_called_once_with(extension)
        extension_notifier_edited.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.extension.notifier.edited')
    @patch('xivo_dao.data_handler.extension.dao.edit')
    @patch('xivo_dao.data_handler.extension.validator.validate_edit')
    def test_edit_with_error_from_dao(self, validate_edit, extension_dao_edit, extension_notifier_edited):
        exten = '1000'
        context = 'toto'

        extension = Extension(exten=exten,
                              context=context)

        error = Exception("message")
        extension_dao_edit.side_effect = ElementCreationError(error, '')

        self.assertRaises(ElementCreationError, extension_services.edit, extension)

    @patch('xivo_dao.data_handler.extension.notifier.deleted')
    @patch('xivo_dao.data_handler.extension.dao.delete')
    @patch('xivo_dao.data_handler.extension.validator.validate_delete')
    def test_delete(self, validate_delete, extension_dao_delete, extension_notifier_deleted):
        exten = 'extension'
        context = 'toto'
        extension = Extension(id=1,
                              exten=exten,
                              context=context)

        extension_services.delete(extension)

        validate_delete.assert_called_once_with(extension)
        extension_dao_delete.assert_called_once_with(extension)
        extension_notifier_deleted.assert_called_once_with(extension)
