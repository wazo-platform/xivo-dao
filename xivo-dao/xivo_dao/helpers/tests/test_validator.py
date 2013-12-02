# -*- coding: utf-8 -*-
#
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

from mock import Mock, patch
from hamcrest import *
from unittest import TestCase

from xivo_dao.helpers import validator


class TestValidator(TestCase):

    def test_is_positive_number(self):
        res = validator.is_positive_number('toto')
        assert_that(res, equal_to(False))

        res = validator.is_positive_number('-445')
        assert_that(res, equal_to(False))

        res = validator.is_positive_number(-445)
        assert_that(res, equal_to(False))

        res = validator.is_positive_number(35.4)
        assert_that(res, equal_to(False))

        res = validator.is_positive_number('0000')
        assert_that(res, equal_to(True))

        res = validator.is_positive_number('12345')
        assert_that(res, equal_to(True))

        res = validator.is_positive_number(1234)
        assert_that(res, equal_to(True))

    @patch('xivo_dao.data_handler.context.services.find_by_name')
    def test_is_existing_context(self, mock_find):
        expected_return = mock_find.return_value = Mock()

        result = validator.is_existing_context('abcd')

        mock_find.assert_called_once_with('abcd')
        assert_that(result, same_instance(expected_return))
