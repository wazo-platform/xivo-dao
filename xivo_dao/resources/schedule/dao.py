# -*- coding: utf-8 -*-

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

from xivo_dao.helpers.db_manager import daosession

from .persistor import SchedulePersistor
from .search import schedule_search


@daosession
def search(session, **parameters):
    return SchedulePersistor(session, schedule_search).search(parameters)


@daosession
def get(session, schedule_id):
    return SchedulePersistor(session, schedule_search).get_by({'id': schedule_id})


@daosession
def get_by(session, **criteria):
    return SchedulePersistor(session, schedule_search).get_by(criteria)


@daosession
def find(session, schedule_id):
    return SchedulePersistor(session, schedule_search).find_by({'id': schedule_id})


@daosession
def find_by(session, **criteria):
    return SchedulePersistor(session, schedule_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SchedulePersistor(session, schedule_search).find_all_by(criteria)


@daosession
def create(session, schedule):
    return SchedulePersistor(session, schedule_search).create(schedule)


@daosession
def edit(session, schedule):
    SchedulePersistor(session, schedule_search).edit(schedule)


@daosession
def delete(session, schedule):
    SchedulePersistor(session, schedule_search).delete(schedule)
