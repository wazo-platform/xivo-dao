# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.contextnumbers import ContextNumbers


class TestContextNumbers(unittest.TestCase):

    def test_in_range(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('1500'))

    def test_in_range_when_outside(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('2000'), equal_to(False))

    def test_in_range_with_no_end(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         numberend='',
                                         did_length=0)

        assert_that(context_numbers.in_range('1000'))

    def test_in_range_with_no_end_when_outside(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         numberend='',
                                         did_length=0)

        assert_that(context_numbers.in_range('1001'), equal_to(False))

    def test_in_range_when_negative(self):
        context_numbers = ContextNumbers(context='toto',
                                         type='incall',
                                         start='1000',
                                         end='1999',
                                         did_length=0)

        assert_that(context_numbers.in_range('-1500'), equal_to(False))
