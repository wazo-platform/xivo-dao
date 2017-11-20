# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
