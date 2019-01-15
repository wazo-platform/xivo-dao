# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.paging import Paging

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class PagingPersistor(CriteriaBuilderMixin):

    _search_table = Paging

    def __init__(self, session, paging_search, tenant_uuids=None):
        self.session = session
        self.paging_search = paging_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Paging)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        paging = self.find_by(criteria)
        if not paging:
            raise errors.not_found('Paging', **criteria)
        return paging

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.paging_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.paging_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Paging.tenant_uuid.in_(self.tenant_uuids))

    def create(self, paging):
        self.session.add(paging)
        self.session.flush()
        return paging

    def edit(self, paging):
        self.session.add(paging)
        self.session.flush()

    def delete(self, paging):
        self.session.delete(paging)
        self.session.flush()
