# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random

from xivo_dao.alchemy.meeting import Meeting, MeetingOwner
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult

NUMBER_LEN = 6


class Persistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Meeting

    def __init__(self, session, search_system, tenant_uuids=None):
        self.session = session
        self.search_system = search_system
        self.tenant_uuids = tenant_uuids

    def create(self, meeting):
        meeting.number = self._generate_number()
        self.session.add(meeting)
        self.session.flush()
        return meeting

    def search(self, parameters):
        query = self._search_query()
        query = self._filter_tenant_uuid(query)
        query = self._filter_owner(query, parameters)
        query = self._filter_created_before(query, parameters)
        rows, total = self.search_system.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_owner(self, query, criteria):
        owner = criteria.pop('owner', None)
        if not owner:
            return query

        owner_meeting = self.session.query(
            MeetingOwner.meeting_uuid
        ).filter(MeetingOwner.user_uuid == owner)
        query = query.filter(Meeting.uuid.in_(owner_meeting))

        return query

    def _filter_created_before(self, query, criteria):
        before = criteria.pop('created_before', None)
        if not before:
            return query

        return query.filter(Meeting.created_at < before)

    def _find_query(self, criteria):
        query = self.session.query(Meeting)
        query = self._filter_tenant_uuid(query)
        query = self._filter_owner(query, criteria)
        query = self._filter_created_before(query, criteria)
        return self.build_criteria(query, criteria)

    def _generate_number(self):
        max = int('9' * NUMBER_LEN)
        while True:
            number = str(random.randint(0, max)).rjust(NUMBER_LEN, '0')
            count = self.session.query(Meeting).filter(Meeting.number == number).count()
            if not count:
                return number

    def _search_query(self):
        return self.session.query(self.search_system.config.table)
