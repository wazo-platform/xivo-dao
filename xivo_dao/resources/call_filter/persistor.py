# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CallFilterPersistor(CriteriaBuilderMixin):

    _search_table = CallFilter

    def __init__(self, session, call_filter_search, tenant_uuids=None):
        self.session = session
        self.call_filter_search = call_filter_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(CallFilter)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        call_filter = self.find_by(criteria)
        if not call_filter:
            raise errors.not_found('CallFilter', **criteria)
        return call_filter

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.call_filter_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.call_filter_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(CallFilter.tenant_uuid.in_(self.tenant_uuids))

    def create(self, call_filter):
        self._fill_default_values(call_filter)
        self.session.add(call_filter)
        self.session.flush()
        return call_filter

    def edit(self, call_filter):
        self.session.add(call_filter)
        self.session.flush()

    def delete(self, call_filter):
        self.session.delete(call_filter)
        self.session.flush()

    def _fill_default_values(self, call_filter):
        call_filter.type = 'bosssecretary'

    def associate_recipients(self, call_filter, recipients):
        for recipient in recipients:
            self._fill_default_recipient_values(recipient)
        call_filter.recipients = recipients
        self.session.flush()

    def _fill_default_recipient_values(self, recipient):
        recipient.type = 'user'
        recipient.bstype = 'boss'

    def associate_surrogates(self, call_filter, surrogates):
        for surrogate in surrogates:
            self._fill_default_surrogate_values(surrogate)
        call_filter.surrogates = surrogates
        self.session.flush()

    def _fill_default_surrogate_values(self, surrogate):
        surrogate.type = 'user'
        surrogate.bstype = 'secretary'

    def update_fallbacks(self, call_filter, fallbacks):
        for event in list(call_filter.callfilter_dialactions.keys()):
            if event not in fallbacks:
                call_filter.callfilter_dialactions.pop(event, None)

        for event, dialaction in fallbacks.items():
            if dialaction is None:
                call_filter.callfilter_dialactions.pop(event, None)
                continue

            if event not in call_filter.callfilter_dialactions:
                dialaction.category = 'callfilter'
                dialaction.event = event
                call_filter.callfilter_dialactions[event] = dialaction

            call_filter.callfilter_dialactions[event].action = dialaction.action
            call_filter.callfilter_dialactions[event].actionarg1 = dialaction.actionarg1
            call_filter.callfilter_dialactions[event].actionarg2 = dialaction.actionarg2

        self.session.flush()
