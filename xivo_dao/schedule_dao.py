# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import commit_or_abort


@daosession
def add(session, schedule):
    with commit_or_abort(session):
        session.add(schedule)


@daosession
def add_user_to_schedule(session, userid, scheduleid, order=0):
    schedulepath = SchedulePath()
    schedulepath.path = 'user'
    schedulepath.schedule_id = scheduleid
    schedulepath.pathid = userid
    schedulepath.order = order

    with commit_or_abort(session):
        session.add(schedulepath)


@daosession
def get_schedules_for_user(session, userid):
    return session.query(Schedule).join((SchedulePath, SchedulePath.schedule_id == Schedule.id))\
                                  .filter(SchedulePath.path == 'user')\
                                  .filter(SchedulePath.pathid == userid)\
                                  .all()


@daosession
def remove_user_from_all_schedules(session, userid):
    with commit_or_abort(session):
        session.query(SchedulePath).filter(SchedulePath.path == 'user')\
                                   .filter(SchedulePath.pathid == userid)\
                                   .delete()
