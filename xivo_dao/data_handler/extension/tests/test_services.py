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
from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.extension import services as extension_services


class TestExtension(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.search')
    def test_search(self, search_dao):
        search_result = search_dao.return_value = Mock(SearchResult)

        result = extension_services.search(search='term', order='exten',
                                           direction='desc', skip=1,
                                           limit=2)

        search_dao.assert_called_once_with(search='term', order='exten',
                                           direction='desc', skip=1,
                                           limit=2)
        assert_that(result, equal_to(search_result))

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    def test_find_by_exten_context(self, find_by_exten_context):
        expected = Extension(exten='1000', context='default')

        find_by_exten_context.return_value = expected

        result = extension_services.find_by_exten_context(expected.exten, expected.context)

        find_by_exten_context.assert_called_once_with(expected.exten, expected.context)
        assert_that(result, equal_to(expected))

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

        assert_that(result, equal_to(extension))
        validate_create.assert_called_once_with(extension)
        extension_dao_create.assert_called_once_with(extension)
        extension_notifier_created.assert_called_once_with(extension)

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


@patch('xivo_dao.data_handler.line.dao.associate_extension')
@patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
@patch('xivo_dao.data_handler.extension.notifier.edited')
@patch('xivo_dao.data_handler.extension.dao.edit')
@patch('xivo_dao.data_handler.extension.validator.validate_edit')
class TestExtensionEdit(TestCase):

    def test_given_no_line_extension_then_only_extension_edited(self,
                                                                validate_edit,
                                                                extension_dao_edit,
                                                                extension_notifier_edited,
                                                                find_by_extension_id,
                                                                associate_extension):
        exten = '1000'
        context = 'toto'

        extension = Extension(id=1,
                              exten=exten,
                              context=context)

        extension_dao_edit.return_value = extension
        find_by_extension_id.return_value = None

        extension_services.edit(extension)

        validate_edit.assert_called_once_with(extension)
        extension_dao_edit.assert_called_once_with(extension)
        extension_notifier_edited.assert_called_once_with(extension)
        find_by_extension_id.assert_called_once_with(extension.id)
        self.assertNotCalled(associate_extension)

    def test_given_line_extension_then_line_updated(self,
                                                    validate_edit,
                                                    extension_dao_edit,
                                                    extension_notifier_edited,
                                                    find_by_extension_id,
                                                    associate_extension):
        exten = '1000'
        context = 'toto'

        extension = Extension(id=1,
                              exten=exten,
                              context=context)

        line_extension = LineExtension(extension_id=1,
                                       line_id=2)

        extension_dao_edit.return_value = extension
        find_by_extension_id.return_value = line_extension

        extension_services.edit(extension)

        validate_edit.assert_called_once_with(extension)
        extension_dao_edit.assert_called_once_with(extension)
        extension_notifier_edited.assert_called_once_with(extension)
        find_by_extension_id.assert_called_once_with(extension.id)
        associate_extension.assert_called_once_with(extension, line_extension.line_id)
