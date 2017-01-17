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

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      equal_to,
                      none,
                      not_)

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase


class TestIncalls(DAOTestCase):

    def test_getter(self):
        incall = self.add_incall()
        schedule = self.add_schedule()
        self.add_schedule_path(path='incall', pathid=incall.id, schedule_id=schedule.id)

        row = self.session.query(Incall).filter_by(id=incall.id).first()
        assert_that(row, equal_to(incall))
        assert_that(row.schedules, contains(schedule))

    def test_setter(self):
        incall = self.add_incall()
        schedule1 = Schedule()
        schedule2 = Schedule()
        incall.schedules = [schedule1, schedule2]

        row = self.session.query(Incall).filter_by(id=incall.id).first()
        assert_that(row, equal_to(incall))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        incall = self.add_incall()
        schedule1 = Schedule()
        schedule2 = Schedule()
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


class TestDelete(DAOTestCase):

    def test_schedule_paths_are_deleted(self):
        incall = self.add_incall()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='incall', pathid=incall.id)

        self.session.delete(schedule)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())
