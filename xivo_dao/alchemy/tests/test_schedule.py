# -*- coding: utf-8 -*-
#
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that,
                      contains,
                      empty,
                      equal_to,
                      none)

from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedule_time import ScheduleTime
from xivo_dao.tests.test_dao import DAOTestCase


class TestOpenPeriods(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        open_period = self.add_schedule_time(mode='opened', schedule_id=schedule.id)
        self.add_schedule_time(mode='closed', schedule_id=schedule.id)

        assert_that(schedule.open_periods, contains(open_period))

    def test_setter(self):
        schedule = self.add_schedule()
        open_period = self.add_schedule_time(mode='opened')

        schedule.open_periods = [open_period]
        self.session.flush()

        assert_that(schedule.open_periods, contains(open_period))
        assert_that(schedule.exceptional_periods, empty())

    def test_setter_to_empty(self):
        schedule = self.add_schedule()
        self.add_schedule_time(mode='opened', schedule_id=schedule.id)
        exceptional_period = self.add_schedule_time(mode='closed', schedule_id=schedule.id)

        schedule.open_periods = []
        self.session.flush()

        assert_that(schedule.open_periods, empty())
        assert_that(schedule.exceptional_periods, contains(exceptional_period))


class TestExceptionalPeriods(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        exceptional_period = self.add_schedule_time(mode='closed', schedule_id=schedule.id)
        self.add_schedule_time(mode='opened', schedule_id=schedule.id)

        assert_that(schedule.exceptional_periods, contains(exceptional_period))

    def test_setter(self):
        schedule = self.add_schedule()
        exceptional_period = self.add_schedule_time(mode='closed')

        schedule.exceptional_periods = [exceptional_period]
        self.session.flush()

        assert_that(schedule.exceptional_periods, contains(exceptional_period))
        assert_that(schedule.open_periods, empty())

    def test_setter_to_empty(self):
        schedule = self.add_schedule()
        self.add_schedule_time(mode='closed', schedule_id=schedule.id)
        open_period = self.add_schedule_time(mode='opened', schedule_id=schedule.id)

        schedule.exceptional_periods = []
        self.session.flush()

        assert_that(schedule.exceptional_periods, empty())
        assert_that(schedule.open_periods, contains(open_period))


class TestType(unittest.TestCase):

    def test_getter(self):
        schedule = Schedule(fallback_action='endcall:hangup')
        assert_that(schedule.type, equal_to('endcall'))

    def test_getter_no_subtype(self):
        schedule = Schedule(fallback_action='user')
        assert_that(schedule.type, equal_to('user'))

    def test_getter_none(self):
        schedule = Schedule(fallback_action=None)
        assert_that(schedule.type, equal_to(None))

    def test_setter(self):
        schedule = Schedule(type='user')
        assert_that(schedule.fallback_action, equal_to('user'))

    def test_setter_when_subtype(self):
        schedule = Schedule(type='endcall', subtype='hangup')
        assert_that(schedule.fallback_action, equal_to('endcall:hangup'))

    def test_setter_none(self):
        schedule = Schedule(type=None)
        assert_that(schedule.fallback_action, equal_to(''))


class TestSubtype(unittest.TestCase):

    def test_getter(self):
        schedule = Schedule(fallback_action='endcall:hangup')
        assert_that(schedule.subtype, equal_to('hangup'))

    def test_getter_no_type(self):
        schedule = Schedule(fallback_action=':hangup')
        assert_that(schedule.subtype, equal_to('hangup'))

    def test_getter_none(self):
        schedule = Schedule(fallback_action=None)
        assert_that(schedule.subtype, equal_to(None))

    def test_setter(self):
        schedule = Schedule(subtype='hangup')
        assert_that(schedule.fallback_action, equal_to(':hangup'))

    def test_setter_when_type(self):
        schedule = Schedule(type='endcall', subtype='hangup')
        assert_that(schedule.fallback_action, equal_to('endcall:hangup'))

    def test_setter_none(self):
        schedule = Schedule(subtype=None)
        assert_that(schedule.fallback_action, equal_to(''))


class TestEnabled(unittest.TestCase):

    def test_getter_true(self):
        schedule = Schedule(commented=0)
        assert_that(schedule.enabled, equal_to(True))

    def test_getter_false(self):
        schedule = Schedule(commented=1)
        assert_that(schedule.enabled, equal_to(False))

    def test_setter_true(self):
        schedule = Schedule(enabled=True)
        assert_that(schedule.commented, equal_to(0))

    def test_setter_false(self):
        schedule = Schedule(enabled=False)
        assert_that(schedule.commented, equal_to(1))


class TestDelete(DAOTestCase):

    def test_periods_are_deleted(self):
        schedule = self.add_schedule()
        self.add_schedule_time(mode='opened', schedule_id=schedule.id)
        self.add_schedule_time(mode='closed', schedule_id=schedule.id)

        self.session.delete(schedule)
        self.session.flush()

        row = self.session.query(ScheduleTime).first()
        assert_that(row, none())
