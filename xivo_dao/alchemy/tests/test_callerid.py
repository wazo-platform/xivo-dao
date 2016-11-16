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

from hamcrest import (assert_that,
                      equal_to)

from xivo_dao.tests.test_dao import DAOTestCase


class TestName(DAOTestCase):

    def test_getter(self):
        callerid = self.add_callerid(callerdisplay='Bob')

        assert_that(callerid.name, equal_to('Bob'))

    def test_getter_when_empty_string(self):
        callerid = self.add_callerid(callerdisplay='')

        assert_that(callerid.name, equal_to(None))

    def test_setter(self):
        callerid = self.add_callerid(callerdisplay='')
        callerid.name = 'Bob'

        assert_that(callerid.callerdisplay, equal_to('Bob'))

    def test_setter_to_none(self):
        callerid = self.add_callerid(callerdisplay='Bob')
        callerid.name = None

        assert_that(callerid.callerdisplay, equal_to(''))
