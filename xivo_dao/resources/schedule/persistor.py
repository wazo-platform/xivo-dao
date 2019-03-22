# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SchedulePersistor(CriteriaBuilderMixin):

    _search_table = Schedule

    def __init__(self, session, schedule_search, tenant_uuids=None):
        self.session = session
        self.schedule_search = schedule_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Schedule)
        query = self._filter_tenant_uuid(query)
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
        query = self.session.query(self.schedule_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.schedule_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Schedule.tenant_uuid.in_(self.tenant_uuids))

    def create(self, schedule):
        self.session.add(schedule)
        self.session.flush()
        return schedule

    def edit(self, schedule):
        self.session.add(schedule)
        self.session.flush()

    def delete(self, schedule):
        self.session.delete(schedule)
        self.session.flush()
