# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, equal_to
from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.tests.test_dao import DAOTestCase


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


class TestExten(DAOTestCase):

    def test_getter(self):
        parking_lot = self.add_parking_lot()
        extension = self.add_extension(type='parking', typeval=parking_lot.id)

        assert_that(parking_lot.exten, equal_to(extension.exten))

    def test_expression(self):
        parking_lot = self.add_parking_lot()
        extension = self.add_extension(type='parking', typeval=parking_lot.id)

        result = (
            self.session.query(ParkingLot)
            .filter(ParkingLot.exten == extension.exten)
            .first()
        )

        assert_that(result, equal_to(parking_lot))
        assert_that(result.exten, equal_to(extension.exten))
