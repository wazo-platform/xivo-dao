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

from mock import patch, Mock

from xivo_dao.tests.test_case import TestCase
from xivo_dao.data_handler.func_key import validator
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import NonexistentParametersError


class TestFuncKeyValidateCreate(TestCase):

    @patch('xivo_dao.data_handler.func_key.validator.validate_type')
    @patch('xivo_dao.data_handler.func_key.validator.validate_destination')
    @patch('xivo_dao.data_handler.func_key.validator.validate_missing_parameters')
    def test_validate_create(self, validate_missing_parameters, validate_type, validate_destination):
        func_key = Mock(FuncKey)

        validator.validate_create(func_key)

        validate_missing_parameters.assert_called_once_with(func_key)
        validate_type.assert_called_once_with(func_key)
        validate_destination.assert_called_once_with(func_key)


class TestFuncKeyValidateMissingParameters(TestCase):

    def test_when_no_parameters_then_raises_error(self):
        func_key = FuncKey()

        self.assertRaisesRegexp(MissingParametersError,
                                "Missing parameters: type,destination,destination_id",
                                validator.validate_missing_parameters,
                                func_key)

    def test_when_all_parameters_then_validation_passes(self):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        validator.validate_missing_parameters(func_key)


@patch('xivo_dao.data_handler.func_key.type_dao.find_type_for_name')
class TestFuncKeyValidateType(TestCase):

    def test_when_unknown_type_then_raises_error(self, dao_find_type_for_name):
        func_key = Mock(FuncKey, type='superdupertype')
        dao_find_type_for_name.return_value = None

        self.assertRaisesRegexp(InvalidParametersError,
                                "Invalid parameters: type superdupertype does not exist",
                                validator.validate_type,
                                func_key)
        dao_find_type_for_name.assert_called_once_with(func_key.type)

    def test_when_find_type_for_name_then_validation_passes(self, dao_find_type_for_name):
        func_key = Mock(FuncKey, type='speeddial')
        dao_find_type_for_name.return_value = Mock()

        validator.validate_type(func_key)
        dao_find_type_for_name.assert_called_once_with(func_key.type)


class TestFuncKeyValidateDestination(TestCase):

    @patch('xivo_dao.data_handler.func_key.validator.validate_destination_type')
    @patch('xivo_dao.data_handler.func_key.validator.validate_destination_exists')
    def test_validate_destination(self, validate_destination_type, validate_destination_exists):
        func_key = Mock(FuncKey)

        validator.validate_destination(func_key)

        validate_destination_type.assert_called_once_with(func_key)
        validate_destination_exists.assert_called_once_with(func_key)


@patch('xivo_dao.data_handler.func_key.type_dao.find_destination_type_for_name')
class TestFuncKeyValidateDestinationType(TestCase):

    def test_when_destination_type_does_not_exists_then_raises_error(self,
                                                                     find_destination_type_for_name):
        find_destination_type_for_name.return_value = None
        func_key = Mock(FuncKey, destination='superdestination')

        self.assertRaisesRegexp(InvalidParametersError,
                                "Invalid parameters: destination of type superdestination does not exist",
                                validator.validate_destination_type,
                                func_key)
        find_destination_type_for_name.assert_called_once_with(func_key.destination)

    def test_when_find_destination_type_for_name_then_validation_passes(self,
                                                                        find_destination_type_for_name):
        find_destination_type_for_name.return_value = Mock()
        func_key = Mock(FuncKey, destination='user')

        validator.validate_destination_type(func_key)
        find_destination_type_for_name.assert_called_once_with(func_key.destination)


@patch('xivo_dao.data_handler.user.dao.get')
class TestFuncKeyDestinationExists(TestCase):

    def test_when_user_destination_does_not_exist_then_raises_error(self, user_dao_get):
        user_dao_get.side_effect = ElementNotExistsError('User')
        func_key = Mock(FuncKey, destination='user', destination_id=1)

        self.assertRaisesRegexp(NonexistentParametersError,
                                "Nonexistent parameters: user 1 does not exist",
                                validator.validate_destination_exists,
                                func_key)
        user_dao_get.assert_called_once_with(func_key.destination_id)

    def test_when_user_destination_exists_then_validation_passes(self, user_dao_get):
        user_dao_get.return_value = Mock()
        func_key = Mock(FuncKey, destination='user', destination_id=1)

        validator.validate_destination_exists(func_key)
        user_dao_get.assert_called_once_with(func_key.destination_id)
