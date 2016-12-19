# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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
from xivo_dao.alchemy.parking_lot import ParkingLot


class TestInSlotsRange(unittest.TestCase):

    def setUp(self):
        self.parking_lot = ParkingLot(slots_start='701', slots_end='750')

    def test_in_range(self):
        result = self.parking_lot.in_slots_range(725)
        assert_that(result, equal_to(True))

    def test_in_range_str(self):
        result = self.parking_lot.in_slots_range('725')
        assert_that(result, equal_to(True))

    def test_limit_start_range(self):
        result = self.parking_lot.in_slots_range(701)
        assert_that(result, equal_to(True))

    def test_limit_end_range(self):
        result = self.parking_lot.in_slots_range(750)
        assert_that(result, equal_to(True))

    def test_before_range(self):
        result = self.parking_lot.in_slots_range(699)
        assert_that(result, equal_to(False))

    def test_after_range(self):
        result = self.parking_lot.in_slots_range(800)
        assert_that(result, equal_to(False))
