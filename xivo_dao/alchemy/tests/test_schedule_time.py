# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, equal_to


from xivo_dao.alchemy.schedule_time import ScheduleTime


class TestHoursStart(unittest.TestCase):

    def test_getter(self):
        schedule_time = ScheduleTime(hours='07:15-08:15')
        assert_that(schedule_time.hours_start, equal_to('07:15'))

    def test_getter_no_hours_end(self):
        schedule_time = ScheduleTime(hours='07:15')
        assert_that(schedule_time.hours_start, equal_to('07:15'))

    def test_getter_none(self):
        schedule_time = ScheduleTime(hours=None)
        assert_that(schedule_time.hours_start, equal_to(None))

    def test_setter(self):
        schedule_time = ScheduleTime(hours_start='07:15')
        assert_that(schedule_time.hours, equal_to('07:15'))

    def test_setter_when_hours_end(self):
        schedule_time = ScheduleTime(hours_start='07:15', hours_end='08:15')
        assert_that(schedule_time.hours, equal_to('07:15-08:15'))

    def test_setter_none(self):
        schedule_time = ScheduleTime(hours_start=None)
        assert_that(schedule_time.hours, equal_to(''))


class TestHoursEnd(unittest.TestCase):

    def test_getter(self):
        schedule_time = ScheduleTime(hours='07:15-08:15')
        assert_that(schedule_time.hours_end, equal_to('08:15'))

    def test_getter_no_hours_start(self):
        schedule_time = ScheduleTime(hours='-08:15')
        assert_that(schedule_time.hours_end, equal_to('08:15'))

    def test_getter_none(self):
        schedule_time = ScheduleTime(hours=None)
        assert_that(schedule_time.hours_end, equal_to(None))

    def test_setter(self):
        schedule_time = ScheduleTime(hours_end='08:15')
        assert_that(schedule_time.hours, equal_to('-08:15'))

    def test_setter_when_hours_start(self):
        schedule_time = ScheduleTime(hours_start='07:15', hours_end='08:15')
        assert_that(schedule_time.hours, equal_to('07:15-08:15'))

    def test_setter_none(self):
        schedule_time = ScheduleTime(hours_end=None)
        assert_that(schedule_time.hours, equal_to(''))


class TestWeekDays(unittest.TestCase):

    def test_getter_mix_range(self):
        schedule_time = ScheduleTime(weekdays='1,4-7,10')
        assert_that(schedule_time.week_days, equal_to([1, 4, 5, 6, 7, 10]))

    def test_getter_none(self):
        schedule_time = ScheduleTime(weekdays=None)
        assert_that(schedule_time.week_days, equal_to(
            [1, 2, 3, 4, 5, 6, 7]
        ))

    def test_setter_mix_range(self):
        schedule_time = ScheduleTime(week_days=[1, 3, 5, 6])
        assert_that(schedule_time.weekdays, equal_to('1,3,5,6'))

    def test_setter_none(self):
        schedule_time = ScheduleTime(week_days=None)
        assert_that(schedule_time.weekdays, equal_to(None))


class TestMonthDays(unittest.TestCase):

    def test_getter_mix_range(self):
        schedule_time = ScheduleTime(monthdays='1,4-7,10')
        assert_that(schedule_time.month_days, equal_to([1, 4, 5, 6, 7, 10]))

    def test_getter_none(self):
        schedule_time = ScheduleTime(monthdays=None)
        assert_that(schedule_time.month_days, equal_to(
            [1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31]
        ))

    def test_setter_mix_range(self):
        schedule_time = ScheduleTime(month_days=[1, 3, 5, 6])
        assert_that(schedule_time.monthdays, equal_to('1,3,5,6'))

    def test_setter_none(self):
        schedule_time = ScheduleTime(month_days=None)
        assert_that(schedule_time.monthdays, equal_to(None))


class TestMonthsList(unittest.TestCase):

    def test_getter_mix_range(self):
        schedule_time = ScheduleTime(months='1,4-7,10')
        assert_that(schedule_time.months_list, equal_to([1, 4, 5, 6, 7, 10]))

    def test_getter_none(self):
        schedule_time = ScheduleTime(months=None)
        assert_that(schedule_time.months_list, equal_to(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        ))

    def test_setter_mix_range(self):
        schedule_time = ScheduleTime(months_list=[1, 3, 5, 6])
        assert_that(schedule_time.months, equal_to('1,3,5,6'))

    def test_setter_none(self):
        schedule_time = ScheduleTime(months_list=None)
        assert_that(schedule_time.months, equal_to(None))


class TestType(unittest.TestCase):

    def test_getter(self):
        schedule = ScheduleTime(action='endcall:hangup')
        assert_that(schedule.type, equal_to('endcall'))

    def test_getter_no_subtype(self):
        schedule = ScheduleTime(action='user')
        assert_that(schedule.type, equal_to('user'))

    def test_getter_none(self):
        schedule = ScheduleTime(action=None)
        assert_that(schedule.type, equal_to(None))

    def test_setter(self):
        schedule = ScheduleTime(type='user')
        assert_that(schedule.action, equal_to('user'))

    def test_setter_when_subtype(self):
        schedule = ScheduleTime(type='endcall', subtype='hangup')
        assert_that(schedule.action, equal_to('endcall:hangup'))

    def test_setter_none(self):
        schedule = ScheduleTime(type=None)
        assert_that(schedule.action, equal_to(''))


class TestSubtype(unittest.TestCase):

    def test_getter(self):
        schedule = ScheduleTime(action='endcall:hangup')
        assert_that(schedule.subtype, equal_to('hangup'))

    def test_getter_no_type(self):
        schedule = ScheduleTime(action=':hangup')
        assert_that(schedule.subtype, equal_to('hangup'))

    def test_getter_none(self):
        schedule = ScheduleTime(action=None)
        assert_that(schedule.subtype, equal_to(None))

    def test_setter(self):
        schedule = ScheduleTime(subtype='hangup')
        assert_that(schedule.action, equal_to(':hangup'))

    def test_setter_when_type(self):
        schedule = ScheduleTime(type='endcall', subtype='hangup')
        assert_that(schedule.action, equal_to('endcall:hangup'))

    def test_setter_none(self):
        schedule = ScheduleTime(subtype=None)
        assert_that(schedule.action, equal_to(''))
