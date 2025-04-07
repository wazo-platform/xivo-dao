# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.parking_lot import ParkingLot
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..func_key import FuncKey
from ..func_key_dest_park_position import FuncKeyDestParkPosition
from ..func_key_dest_parking import FuncKeyDestParking


class TestInSlotsRange(unittest.TestCase):
    def setUp(self):
        self.parking_lot = ParkingLot(slots_start='701', slots_end='750')

    def test_in_range(self):
        result = self.parking_lot.in_slots_range(725)
        assert_that(result, equal_to(True))

    def test_in_range_str(self):
        result = self.parking_lot.in_slots_range('725')
        assert_that(result, equal_to(True))

    def test_in_range_str_pattern(self):
        result = self.parking_lot.in_slots_range('_725')
        assert_that(result, equal_to(False))

    def test_in_range_str_char(self):
        result = self.parking_lot.in_slots_range('*725')
        assert_that(result, equal_to(False))

    def test_in_range_str_beginning_zero(self):
        result = self.parking_lot.in_slots_range('0725')
        assert_that(result, equal_to(False))

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


class TestContext(DAOTestCase):
    def test_getter(self):
        parking_lot = self.add_parking_lot()
        extension = self.add_extension(type='parking', typeval=parking_lot.id)

        assert_that(parking_lot.context, equal_to(extension.context))

    def test_expression(self):
        parking_lot = self.add_parking_lot()
        extension = self.add_extension(type='parking', typeval=parking_lot.id)

        result = (
            self.session.query(ParkingLot)
            .filter(ParkingLot.context == extension.context)
            .first()
        )

        assert_that(result, equal_to(parking_lot))
        assert_that(result.context, equal_to(extension.context))


class TestDelete(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_funckeys_park_position_are_deleted(self):
        parking_lot = self.add_parking_lot()
        self.add_park_position_destination(parking_lot.id, position='801')

        self.session.delete(parking_lot)
        self.session.flush()

        row = self.session.query(FuncKey).first()
        assert_that(row, none())

        row = self.session.query(FuncKeyDestParkPosition).first()
        assert_that(row, none())

    def test_funckeys_parking_are_deleted(self):
        parking_lot = self.add_parking_lot()
        self.add_parking_destination(parking_lot.id)

        self.session.delete(parking_lot)
        self.session.flush()

        row = self.session.query(FuncKey).first()
        assert_that(row, none())

        row = self.session.query(FuncKeyDestParking).first()
        assert_that(row, none())
