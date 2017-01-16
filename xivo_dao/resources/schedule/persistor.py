# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.schedule import Schedule

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin
from xivo_dao.alchemy.entity import Entity


class SchedulePersistor(CriteriaBuilderMixin):

    _search_table = Schedule

    def __init__(self, session, schedule_search):
        self.session = session
        self.schedule_search = schedule_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Schedule)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        schedule = self.find_by(criteria)
        if not schedule:
            raise errors.not_found('Schedule', **criteria)
        return schedule

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.schedule_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, schedule):
        schedule.entity_id = Entity.query_default_id().as_scalar()
        self.session.add(schedule)
        self.session.flush()
        return schedule

    def edit(self, schedule):
        self.session.add(schedule)
        self.session.flush()

    def delete(self, schedule):
        self.session.delete(schedule)
        self.session.flush()
