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

from mock import patch
from hamcrest import *
from unittest import TestCase

from xivo_dao.helpers.validator import is_positive_number


class TestValidator(TestCase):

    def test_is_positive_number(self):
        res = is_positive_number('toto')
        assert_that(res, equal_to(False))

        res = is_positive_number('-445')
        assert_that(res, equal_to(False))

        res = is_positive_number(-445)
        assert_that(res, equal_to(False))

        res = is_positive_number(35.4)
        assert_that(res, equal_to(False))

        res = is_positive_number('0000')
        assert_that(res, equal_to(False))

        res = is_positive_number('12345')
        assert_that(res, equal_to(True))

        res = is_positive_number(1234)
        assert_that(res, equal_to(True))
