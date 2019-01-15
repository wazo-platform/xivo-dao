# -*- coding: utf-8 -*-
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
