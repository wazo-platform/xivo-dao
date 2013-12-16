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
from mock import patch, Mock

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension import validator

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError


class TestValidateAssociate(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.validator.validate_not_associated_to_extension')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_extension')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_line')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_model')
    def test_validate_associate(self,
                                validate_model,
                                validate_line,
                                validate_extension,
                                not_associated_to_extension):

        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        validator.validate_associate(line_extension)

        validate_model.assert_called_once_with(line_extension)
        validate_line.assert_called_once_with(line_extension)
        validate_extension.assert_called_once_with(line_extension)
        not_associated_to_extension.assert_called_once_with(line_extension)


class TestValidateModel(unittest.TestCase):

    def test_validate_model_no_parameters(self):
        line_extension = LineExtension()

        self.assertRaises(MissingParametersError, validator.validate_model, line_extension)


class TestValidateLine(unittest.TestCase):

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_line_when_no_line(self, line_get):
        line_extension = Mock(LineExtension, line_id=1)

        line_get.side_effect = ElementNotExistsError('Line', id=1)

        self.assertRaises(NonexistentParametersError, validator.validate_line, line_extension)
        line_get.assert_called_once_with(line_extension.line_id)

    @patch('xivo_dao.data_handler.line.dao.get')
    def test_validate_line_with_line(self, line_get):
        line_extension = Mock(LineExtension, line_id=1)

        line_get.return_value = line_extension

        validator.validate_line(line_extension)
        line_get.assert_called_once_with(line_extension.line_id)


class TestValidateExtension(unittest.TestCase):

    @patch('xivo_dao.data_handler.extension.dao.get')
    def test_validate_extension_when_no_extension(self, extension_get):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        extension_get.side_effect = ElementNotExistsError('Extension', id=2)

        self.assertRaises(NonexistentParametersError, validator.validate_extension, line_extension)
        extension_get.assert_called_once_with(line_extension.extension_id)

    @patch('xivo_dao.data_handler.extension.dao.get')
    def test_validate_extension_with_extension(self, extension_get):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        extension_get.return_value = line_extension

        validator.validate_extension(line_extension)
        extension_get.assert_called_once_with(line_extension.extension_id)


class TestValidateNotAssociatedToExtension(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_validate_not_associated_to_extension_with_extension(self, find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        find_by_line_id.return_value = Mock()

        self.assertRaises(InvalidParametersError, validator.validate_not_associated_to_extension, line_extension)
        find_by_line_id.assert_called_once_with(line_extension.line_id)

    @patch('xivo_dao.data_handler.line_extension.dao.find_by_line_id')
    def test_validate_not_associated_to_extension_with_no_extension(self, find_by_line_id):
        line_extension = Mock(LineExtension, line_id=1, extension_id=2)

        find_by_line_id.return_value = None

        validator.validate_not_associated_to_extension(line_extension)
        find_by_line_id.assert_called_once_with(line_extension.line_id)


class TestValidateDissociation(unittest.TestCase):

    @patch('xivo_dao.data_handler.user_line_extension.helper.validate_no_device')
    @patch('xivo_dao.data_handler.line_extension.validator.validate_extension')
    def test_validate_dissociation(self, validate_extension, validate_no_device):
        line_extension = Mock(LineExtension, line_id=1)

        validator.validate_dissociation(line_extension)
        validate_extension.assert_called_once_with(line_extension)
        validate_no_device.assert_called_once_with(line_extension.line_id)
