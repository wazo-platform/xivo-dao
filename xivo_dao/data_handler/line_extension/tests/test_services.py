# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from hamcrest import assert_that, equal_to, has_items, none

from xivo_dao.data_handler.context.model import Context, ContextType
from xivo_dao.data_handler.user_line.model import UserLine
from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.incall.model import Incall
from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension import services as line_extension_service
from xivo_dao.data_handler.exception import NotFoundError


@patch('xivo_dao.data_handler.line_extension.notifier.associated')
@patch('xivo_dao.data_handler.line_extension.validator.validate_associate')
@patch('xivo_dao.data_handler.context.dao.get_by_extension_id')
class TestLineExtensionAssociate(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line_extension.services.associate_line_extension')
    def test_given_internal_context_then_creates_line_extension(self,
                                                                associate_line_extension,
                                                                get_by_extension_id,
                                                                validate_associate,
                                                                notifier_associated):

        get_by_extension_id.return_value = Mock(Context, type=ContextType.internal)

        line_extension = Mock(LineExtension, line_id=20, extension_id=30)

        result = line_extension_service.associate(line_extension)

        assert_that(result, equal_to(line_extension))
        validate_associate.assert_called_once_with(line_extension)
        associate_line_extension.assert_called_once_with(line_extension)
        notifier_associated.assert_called_once_with(line_extension)

    @patch('xivo_dao.data_handler.extension.dao.associate_destination')
    @patch('xivo_dao.data_handler.user_line.dao.find_main_user_line')
    @patch('xivo_dao.data_handler.incall.dao.create')
    def test_given_incall_context_then_creates_incall(self,
                                                      incall_dao_create,
                                                      find_main_user_line,
                                                      associate_destination,
                                                      get_by_extension_id,
                                                      validate_associate,
                                                      notifier_associated):

        get_by_extension_id.return_value = Mock(Context, type=ContextType.incall)
        user_line = find_main_user_line.return_value = Mock(UserLine, user_id=10, line_id=20)
        created_incall = incall_dao_create.return_value = Mock(Incall, id=40)

        line_extension = Mock(LineExtension, line_id=20, extension_id=30)
        incall = Incall(destination='user',
                        destination_id=user_line.user_id,
                        extension_id=line_extension.extension_id)

        result = line_extension_service.associate(line_extension)

        assert_that(result, equal_to(line_extension))
        validate_associate.assert_called_once_with(line_extension)
        incall_dao_create.assert_called_once_with(incall)
        associate_destination.assert_called_once_with(line_extension.extension_id, 'incall', created_incall.id)
        notifier_associated.assert_called_once_with(line_extension)


class TestGetByLineId(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.dao.get_by_line_id')
    @patch('xivo_dao.data_handler.line.dao.get')
    def test_get_by_line_id(self, line_get, dao_get_by_line_id):
        line = line_get.return_value = Mock(Line, id=1)
        line_extension = dao_get_by_line_id.return_value = Mock(LineExtension, line_id=line.id)

        result = line_extension_service.get_by_line_id(line.id)

        assert_that(result, equal_to(line_extension))
        line_get.assert_called_once_with(line.id)
        dao_get_by_line_id.assert_called_once_with(line.id)


class TestFindByLineId(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_find_by_line_id(self, dao_find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1)
        dao_find_by_line_id.return_value = line_extension

        result = line_extension_service.find_by_line_id(1)

        assert_that(result, equal_to(line_extension))
        dao_find_by_line_id.assert_called_once_with(1)


class TestFindByExtensionId(unittest.TestCase):

    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_extension_does_not_exist_then_returns_nothing(self, context_find_by_extension_id):
        context_find_by_extension_id.return_value = None

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, none())
        context_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_internal_extension_then_returns_line_extension(self,
                                                                  context_find_by_extension_id,
                                                                  line_extension_find_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='internal')
        line_extension = line_extension_find_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.data_handler.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_incall_extension_then_returns_line_extension(self,
                                                                context_find_by_extension_id,
                                                                find_line_extension_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='incall')
        line_extension = find_line_extension_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)

        result = line_extension_service.find_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        find_line_extension_by_extension_id.assert_called_once_with(2)


class TestGetByExtensionId(unittest.TestCase):

    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_extension_does_not_exist_then_raises_error(self, context_find_by_extension_id):
        context_find_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_internal_extension_then_returns_line_extension(self,
                                                                  context_find_by_extension_id,
                                                                  line_extension_find_by_extension_id):
        line_extension = line_extension_find_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        context_find_by_extension_id.return_value = Mock(Context, type='internal')

        result = line_extension_service.get_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_internal_extension_without_line_then_raises_error(self,
                                                                     context_find_by_extension_id,
                                                                     line_extension_find_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='internal')
        line_extension_find_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)
        line_extension_find_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.data_handler.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_incall_extension_then_returns_line_extension(self,
                                                                context_find_by_extension_id,
                                                                find_line_extension_by_extension_id):
        line_extension = find_line_extension_by_extension_id.return_value = Mock(LineExtension, line_id=1, extension_id=2)
        context_find_by_extension_id.return_value = Mock(Context, type='incall')

        result = line_extension_service.get_by_extension_id(2)

        assert_that(result, equal_to(line_extension))
        context_find_by_extension_id.assert_called_once_with(2)
        find_line_extension_by_extension_id.assert_called_once_with(2)

    @patch('xivo_dao.data_handler.incall.dao.find_line_extension_by_extension_id')
    @patch('xivo_dao.data_handler.context.dao.find_by_extension_id')
    def test_given_incall_extension_without_line_then_raises_error(self,
                                                                   context_find_by_extension_id,
                                                                   find_line_extension_by_extension_id):
        context_find_by_extension_id.return_value = Mock(Context, type='incall')
        find_line_extension_by_extension_id.return_value = None

        self.assertRaises(NotFoundError, line_extension_service.get_by_extension_id, 2)
        find_line_extension_by_extension_id.assert_called_once_with(2)


@patch('xivo_dao.data_handler.context.dao.get_by_extension_id')
@patch('xivo_dao.data_handler.line_extension.notifier.dissociated')
@patch('xivo_dao.data_handler.line_extension.validator.validate_dissociation')
class TestLineExtensionDissociate(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line_extension.services.dissociate_line_extension')
    def test_given_internal_context_then_dissociates_line_extension(self,
                                                                    dissociate_line_extension,
                                                                    validate_dissociation,
                                                                    notifier_dissociated,
                                                                    get_by_extension_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        get_by_extension_id.return_value = Mock(Context, type='internal')

        line_extension_service.dissociate(line_extension)

        get_by_extension_id.assert_called_once_with(line_extension.extension_id)
        validate_dissociation.assert_called_once_with(line_extension)
        dissociate_line_extension.assert_called_once_with(line_extension)
        notifier_dissociated.assert_called_once_with(line_extension)

    @patch('xivo_dao.data_handler.extension.dao.dissociate_extension')
    @patch('xivo_dao.data_handler.incall.dao.delete')
    @patch('xivo_dao.data_handler.incall.dao.find_by_extension_id')
    def test_given_incall_context_then_dissociates_incall(self,
                                                          incall_find_by_extension_id,
                                                          incall_delete,
                                                          dissociate_extension,
                                                          validate_dissociation,
                                                          notifier_dissociated,
                                                          get_by_extension_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        get_by_extension_id.return_value = Mock(Context, type='incall')
        incall = incall_find_by_extension_id.return_value = Mock(Incall)

        line_extension_service.dissociate(line_extension)

        get_by_extension_id.assert_called_once_with(line_extension.extension_id)
        validate_dissociation.assert_called_once_with(line_extension)
        notifier_dissociated.assert_called_once_with(line_extension)
        incall_find_by_extension_id.assert_called_once_with(line_extension.extension_id)
        incall_delete.assert_called_once_with(incall)
        dissociate_extension.assert_called_once_with(line_extension.extension_id)


class TestGetAllByLineId(unittest.TestCase):

    @patch('xivo_dao.data_handler.incall.dao.find_all_line_extensions_by_line_id')
    @patch('xivo_dao.data_handler.line_extension.dao.find_all_by_line_id')
    @patch('xivo_dao.data_handler.line.dao.get')
    def test_get_all_by_line_id(self,
                                line_get,
                                line_extension_find_all_by_line_id,
                                incall_find_all_line_extension_by_line_id):

        line = line_get.return_value = Mock(Line, id=1)
        line_extension = Mock(LineExtension)
        incall_line_extension = Mock(LineExtension)

        line_extension_find_all_by_line_id.return_value = [line_extension]
        incall_find_all_line_extension_by_line_id.return_value = [incall_line_extension]

        result = line_extension_service.get_all_by_line_id(line.id)

        assert_that(result, has_items(line_extension, incall_line_extension))
        line_get.assert_called_once_with(line.id)
        line_extension_find_all_by_line_id.assert_called_once_with(line.id)
        incall_find_all_line_extension_by_line_id.assert_called_once_with(line.id)
