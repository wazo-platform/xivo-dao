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

from xivo_dao.alchemy.dialaction import Dialaction


class TestDialaction(unittest.TestCase):

    def test_gosub_args(self):
        dialaction = Dialaction(action='extension',
                                actionarg1='21',
                                actionarg2='foobar')

        assert_that(dialaction.gosub_args, equal_to('extension,21,foobar'))

    def test_gosub_args_with_none(self):
        dialaction = Dialaction(action='none')

        assert_that(dialaction.gosub_args, equal_to('none,,'))
