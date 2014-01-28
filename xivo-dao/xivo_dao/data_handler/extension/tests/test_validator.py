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

from xivo_dao.data_handler.exception import ElementAlreadyExistsError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.extension import validator
from xivo_dao.data_handler.extension.model import Extension


class TestValidators(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.validator.validate_extension_in_range')
    @patch('xivo_dao.data_handler.extension.validator.validate_extension_available')
    @patch('xivo_dao.data_handler.extension.validator.validate_context_exists')
    @patch('xivo_dao.data_handler.extension.validator.validate_missing_parameters')
    def test_validate_create(self,
                             validate_missing_parameters,
                             validate_context_exists,
                             validate_extension_available,
                             validate_extension_in_range):

        extension = Mock()

        validator.validate_create(extension)

        validate_missing_parameters.assert_called_once_with(extension)
        validate_context_exists.assert_called_once_with(extension)
        validate_extension_available.assert_called_once_with(extension)
        validate_extension_in_range.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.extension.validator.validate_extension_in_range')
    @patch('xivo_dao.data_handler.extension.validator.validate_extension_available')
    @patch('xivo_dao.data_handler.extension.validator.validate_context_exists')
    @patch('xivo_dao.data_handler.extension.validator.validate_missing_parameters')
    def test_validate_edit(self,
                           validate_missing_parameters,
                           validate_context_exists,
                           validate_extension_available,
                           validate_extension_in_range):

        extension = Mock()

        validator.validate_edit(extension)

        validate_missing_parameters.assert_called_once_with(extension)
        validate_context_exists.assert_called_once_with(extension)
        validate_extension_available.assert_called_once_with(extension)
        validate_extension_in_range.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.extension.validator.validate_extension_exists')
    @patch('xivo_dao.data_handler.extension.validator.validate_not_associated_to_line')
    def test_delete(self, validate_extension_exists, validate_not_associated_to_line):
        extension = Mock(Extension)

        validator.validate_delete(extension)

        validate_extension_exists.assert_called_once_with(extension)
        validate_not_associated_to_line.assert_called_once_with(extension)


class TestValidateMissingParameters(unittest.TestCase):

    def test_missing_parameters_when_extension_has_no_parameters(self):
        extension = Extension()

        self.assertRaises(MissingParametersError, validator.validate_missing_parameters, extension)

    def test_missing_parameters_when_extension_has_minimal_parameters(self):
        extension = Extension(exten='1000', context='default')

        validator.validate_missing_parameters(extension)


class TestValidateContextExists(unittest.TestCase):

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    def test_validate_context_exists_when_context_does_not_exist(self, find_by_name):
        find_by_name.return_value = None

        extension = Extension(exten='1000', context='default')

        self.assertRaises(NonexistentParametersError, validator.validate_context_exists, extension)

        find_by_name.assert_called_once_with(extension.context)

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    def test_validate_context_exists_when_context_exists(self, find_by_name):
        find_by_name.return_value = Mock()

        extension = Extension(exten='1000', context='default')

        validator.validate_context_exists(extension)

        find_by_name.assert_called_once_with(extension.context)


class TestValidateExtensionAvailable(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    def test_validate_extension_available_when_extension_does_not_exist(self, find_by_exten_context):
        find_by_exten_context.return_value = None

        extension = Extension(exten='1000', context='default')

        validator.validate_extension_available(extension)

        find_by_exten_context.assert_called_once_with(extension.exten, extension.context)

    @patch('xivo_dao.data_handler.extension.dao.find_by_exten_context')
    def test_validate_extension_available_when_extension_exists(self, find_by_exten_context):
        find_by_exten_context.return_value = Mock(Extension)

        extension = Extension(exten='1000', context='default')

        self.assertRaises(ElementAlreadyExistsError, validator.validate_extension_available, extension)

        find_by_exten_context.assert_called_once_with(extension.exten, extension.context)


class TestValidateExtensionInRange(unittest.TestCase):

    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context')
    def test_validate_extension_in_range_when_extension_outside_of_range(self, is_extension_valid_for_context):
        is_extension_valid_for_context.return_value = False

        extension = Extension(exten='9999', context='default')

        self.assertRaises(InvalidParametersError, validator.validate_extension_in_range, extension)

        is_extension_valid_for_context.assert_called_once_with(extension)

    @patch('xivo_dao.data_handler.context.services.is_extension_valid_for_context')
    def test_validate_extension_in_range_when_extension_inside_of_range(self, is_extension_valid_for_context):
        is_extension_valid_for_context.return_value = True

        extension = Extension(exten='1000', context='default')

        validator.validate_extension_in_range(extension)

        is_extension_valid_for_context.assert_called_once_with(extension)


class TestValidateExtensionExists(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.get')
    def test_validate_extension_exists_when_extension_exists(self, dao_get):
        dao_get.return_value = Mock(Extension)

        extension = Mock(Extension, id=1)

        validator.validate_extension_exists(extension)

        dao_get.assert_called_once_with(extension.id)


class TestValidateExtensionNotAssociatedToLine(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
    def test_validate_not_associated_to_line_when_no_associations(self, find_by_extension_id):
        find_by_extension_id.return_value = None

        extension = Mock(Extension, id=1)

        validator.validate_not_associated_to_line(extension)

        find_by_extension_id.assert_called_once_with(extension.id)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_extension_id')
    def test_validate_not_associated_to_line_when_associated(self, find_by_extension_id):
        find_by_extension_id.return_value = Mock()

        extension = Mock(Extension, id=1)

        self.assertRaises(ElementDeletionError, validator.validate_not_associated_to_line, extension)

        find_by_extension_id.assert_called_once_with(extension.id)
