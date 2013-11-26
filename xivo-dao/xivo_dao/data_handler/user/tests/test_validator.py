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

from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.user import validator
from xivo_dao.data_handler.user.model import User


class TestUserValidator(unittest.TestCase):

    @patch('xivo_dao.data_handler.user.validator.validate_model')
    def test_validate_create(self, validate_model):
        user = Mock(User)

        validator.validate_create(user)
        validate_model.assert_called_once_with(user)

    @patch('xivo_dao.data_handler.user.validator.validate_model')
    def test_validate_edit(self, validate_model):
        user = Mock(User)

        validator.validate_edit(user)
        validate_model.assert_called_once_with(user)

    def test_validate_model_no_properties(self):
        user = User()

        self.assertRaises(MissingParametersError, validator.validate_model, user)

    def test_validate_model_empty_firstname(self):
        firstname = ''

        user = User(firstname=firstname)

        self.assertRaises(InvalidParametersError, validator.validate_model, user)

    def test_validate_model_invalid_password(self):
        password = 'ewrd'

        user = User(firstname='toto',
                    password=password)

        self.assertRaises(InvalidParametersError, validator.validate_model, user)

    def test_validate_model_valid_password(self):
        password = 'ewree'

        user = User(firstname='toto',
                    password=password)

        validator.validate_model(user)

    def test_validate_model_invalid_mobilephonenumber(self):
        user = User(firstname='toto')

        user.mobilephonenumber = 'mobilephonenumber'
        self.assertRaises(InvalidParametersError, validator.validate_model, user)

        user.mobilephonenumber = 'abcd1234'
        self.assertRaises(InvalidParametersError, validator.validate_model, user)

    def test_validate_model_valid_mobilephonenumber(self):
        user = User(firstname='toto')
        user.mobilephonenumber = '1234'

        validator.validate_model(user)
