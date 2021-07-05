# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.orm import joinedload

from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SwitchboardPersistor(CriteriaBuilderMixin):

    _search_table = Switchboard

    def __init__(self, session, switchboard_search, tenant_uuids=None):
        self.session = session
        self.switchboard_search = switchboard_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Switchboard)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _joinedload_query(self):
        return (self.session.query(Switchboard)
                .options(joinedload('incall_dialactions')
                         .joinedload('incall')))

    def get_by(self, criteria):
        switchboard = self.find_by(criteria)
        if not switchboard:
            raise errors.not_found('Switchboard', **criteria)
        return switchboard

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Switchboard.tenant_uuid.in_(self.tenant_uuids))

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.switchboard_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.switchboard_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()
        return switchboard

    def edit(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()

    def delete(self, switchboard):
        self.session.delete(switchboard)
        self.session.flush()
