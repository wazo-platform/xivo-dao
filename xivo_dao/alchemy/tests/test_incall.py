# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
    none,
    not_,
)

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase


class TestSchedules(DAOTestCase):

    def test_getter(self):
        incall = self.add_incall()
        schedule = self.add_schedule()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Incall).filter_by(id=incall.id).first()
        assert_that(row, equal_to(incall))
        assert_that(row.schedules, contains_exactly(schedule))

    def test_setter(self):
        incall = self.add_incall()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        incall.schedules = [schedule1, schedule2]

        row = self.session.query(Incall).filter_by(id=incall.id).first()
        assert_that(row, equal_to(incall))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        incall = self.add_incall()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        incall.schedules = [schedule1, schedule2]
        self.session.flush()

        incall.schedules = []

        row = self.session.query(Incall).filter_by(id=incall.id).first()
        assert_that(row, equal_to(incall))
        assert_that(row.schedules, empty())

        row = self.session.query(Schedule).first()
        assert_that(row, not_(none()))

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())


class TestDestination(DAOTestCase):
    def test_getter_when_no_dialaction(self):
        incall = self.add_incall(destination=None)

        assert_that(incall.dialaction, equal_to(None))
        assert_that(incall.destination, has_properties(type='none'))


class TestDelete(DAOTestCase):

    def test_schedule_paths_are_deleted(self):
        incall = self.add_incall()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='incall', pathid=incall.id)

        self.session.delete(schedule)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())
