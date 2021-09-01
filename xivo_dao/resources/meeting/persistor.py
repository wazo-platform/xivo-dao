# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.meeting import Meeting
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class Persistor(CriteriaBuilderMixin):

    _search_table = Meeting

    def __init__(self, session, search_system, tenant_uuids=None):
        self.session = session
        self.search_system = search_system
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        return self._find_query(criteria).first()

    def find_all_by(self, criteria):
        return self._find_query(criteria).all()

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            raise errors.not_found('Meeting', **criteria)
        return model

    def search(self, parameters):
        query = self._search_query()
        query = self._filter_tenant_uuid(query)
        rows, total = self.search_system.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, model):
        self.session.add(model)
        self.session.flush()
        return model

    def persist(self, model):
        self.session.add(model)
        self.session.flush()
        self.session.expire(model)

    def edit(self, model):
        self.persist(model)

    def delete(self, model):
        self.session.delete(model)
        self.session.flush()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Meeting.tenant_uuid.in_(self.tenant_uuids))

    def _find_query(self, criteria):
        query = self.session.query(Meeting)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)
