# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    contains,
    empty,
    equal_to,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..schedule import Schedule
from ..schedule_time import ScheduleTime
from ..schedulepath import SchedulePath


class TestIncalls(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        incall = self.add_incall()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.incalls, contains(incall))

    def test_getter_empty_when_other_schedulepath(self):
        schedule = self.add_schedule()
        user = self.add_user()
        self.add_schedule_path(path='user', pathid=user.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.incalls, empty())


class TestGroups(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        group = self.add_group()
        self.add_schedule_path(path='group', pathid=group.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.groups, contains(group))

    def test_getter_empty_when_other_schedulepath(self):
        schedule = self.add_schedule()
        incall = self.add_incall()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.groups, empty())


class TestOutcalls(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        outcall = self.add_outcall()
        self.add_schedule_path(path='outcall', pathid=outcall.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.outcalls, contains(outcall))

    def test_getter_empty_when_other_schedulepath(self):
        schedule = self.add_schedule()
        incall = self.add_incall()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.outcalls, empty())


class TestQueues(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        queue = self.add_queuefeatures()
        self.add_schedule_path(path='queue', pathid=queue.id, schedule_id=schedule.id)

        self.session.expire_all()
        assert_that(schedule.queues, contains(queue))

    def test_getter_empty_when_other_schedulepath(self):
        schedule = self.add_schedule()
        incall = self.add_incall()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        self.session.expire_all()
        assert_that(schedule.queues, empty())


class TestUsers(DAOTestCase):

    def test_getter(self):
        schedule = self.add_schedule()
        user = self.add_user()
        self.add_schedule_path(path='user', pathid=user.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.users, contains(user))

    def test_getter_empty_when_other_schedulepath(self):
        schedule = self.add_schedule()
        incall = self.add_incall()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Schedule).filter_by(id=schedule.id).first()
        assert_that(row, equal_to(schedule))
        assert_that(row.users, empty())


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


class TestActionArg1(unittest.TestCase):

    def test_getter(self):
        schedule = Schedule(fallback_actionid=1)
        assert_that(schedule.actionarg1, equal_to(1))

    def test_getter_none(self):
        schedule = Schedule(fallback_actionid=None)
        assert_that(schedule.actionarg1, equal_to(None))

    def test_getter_empty_string(self):
        schedule = Schedule(fallback_actionid='')
        assert_that(schedule.actionarg1, equal_to(None))


class TestActionArg2(unittest.TestCase):

    def test_getter(self):
        schedule = Schedule(fallback_actionargs=2)
        assert_that(schedule.actionarg2, equal_to(2))

    def test_getter_none(self):
        schedule = Schedule(fallback_actionargs=None)
        assert_that(schedule.actionarg2, equal_to(None))

    def test_getter_empty_string(self):
        schedule = Schedule(fallback_actionargs='')
        assert_that(schedule.actionarg2, equal_to(None))


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

    def test_schedule_paths_are_deleted(self):
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='incall', pathid=1)
        self.add_schedule_path(schedule_id=schedule.id, path='outcall', pathid=2)
        self.add_schedule_path(schedule_id=schedule.id, path='user', pathid=3)
        self.add_schedule_path(schedule_id=schedule.id, path='group', pathid=4)
        self.add_schedule_path(schedule_id=schedule.id, path='queue', pathid=5)
        self.add_schedule_path(schedule_id=schedule.id, path='voicemenu', pathid=6)

        self.session.delete(schedule)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())
