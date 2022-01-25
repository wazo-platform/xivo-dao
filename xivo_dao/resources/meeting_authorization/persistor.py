# -*- coding: utf-8 -*-
# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.meeting_authorization import MeetingAuthorization
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class Persistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = MeetingAuthorization

    def __init__(self, session, search_system, meeting_uuid=None):
        self.session = session
        self.search_system = search_system
        self.meeting_uuid = meeting_uuid

    def search(self, parameters):
        query = self._search_query()
        query = self._filter_meeting_uuid(query)
        query = self._filter_guest_uuid(query, parameters)
        query = self._filter_authorization_uuid(query, parameters)
        query = self._filter_created_before(query, parameters)
        rows, total = self.search_system.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_meeting_uuid(self, query):
        return query.filter(MeetingAuthorization.meeting_uuid == self.meeting_uuid)

    def _filter_guest_uuid(self, query, criteria):
        guest_uuid = criteria.pop('guest_uuid', None)
        if not guest_uuid:
            return query

        return query.filter(MeetingAuthorization.guest_uuid == guest_uuid)

    def _filter_authorization_uuid(self, query, criteria):
        uuid = criteria.pop('uuid', None)
        if not uuid:
            return query

        return query.filter(MeetingAuthorization.uuid == uuid)

    def _filter_created_before(self, query, criteria):
        before = criteria.pop('created_before', None)
        if not before:
            return query

        return query.filter(MeetingAuthorization.created_at < before)

    def _find_query(self, criteria):
        query = self.session.query(MeetingAuthorization)
        query = self._filter_meeting_uuid(query)
        query = self._filter_guest_uuid(query, criteria)
        query = self._filter_authorization_uuid(query, criteria)
        query = self._filter_created_before(query, criteria)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)
