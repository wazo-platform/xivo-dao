# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
from xivo_dao import schedule_dao
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.tests.test_dao import DAOTestCase

class TestScheduleDAO(DAOTestCase):

    tables = [Schedule, SchedulePath]

    def setUp(self):
        self.empty_tables()

    def test_add(self):
        schedule = Schedule()
        schedule.name = 'test'
        schedule_dao.add(schedule)

        self.assertEquals(schedule, self.session.query(Schedule).first())

    def test_add_user_to_schedule(self):
        schedule_dao.add_user_to_schedule(1, 2, 3)
        result = self.session.query(SchedulePath).first()
        self.assertEquals('user', result.path)
        self.assertEquals(1, result.pathid)
        self.assertEquals(2, result.schedule_id)
        self.assertEquals(3, result.order)

    def test_get_schedules_for_user(self):
        scheduleid = self._insert_schedule('test')
        self._add_user_to_schedule(1, scheduleid)
        self._add_user_to_schedule(2, scheduleid)
        result = schedule_dao.get_schedules_for_user(1)
        self.assertEquals(1, len(result))

    def _insert_schedule(self, name):
        schedule = Schedule()
        schedule.name = name
        self.add_me(schedule)
        return schedule.id

    def _add_user_to_schedule(self, userid, scheduleid, order=0):
        schedulepath = SchedulePath()
        schedulepath.path = 'user'
        schedulepath.schedule_id = scheduleid
        schedulepath.pathid = userid
        schedulepath.order = order

        self.add_me(schedulepath)

    def test_remove_user_from_all_schedules(self):
        scheduleid = self._insert_schedule('test')
        self._add_user_to_schedule(1, scheduleid)
        self._add_user_to_schedule(2, scheduleid)

        schedule_dao.remove_user_from_all_schedules(1)
        result = self.session.query(SchedulePath).all()
        self.assertEquals(1, len(result))
        self.assertEquals(2, result[0].pathid)
