# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.helpers import errors
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class Persistor(CriteriaBuilderMixin):

    _search_table = Tenant

    def __init__(self, session, search, tenant_uuids=None):
        self.session = session
        self.resource_search = search
        self.tenant_uuids = tenant_uuids

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def get_by(self, criteria):
        resource = self.find_by(criteria)
        if not resource:
            raise errors.not_found('Tenant', **criteria)
        return resource

    def search(self, parameters):
        query = self.session.query(Tenant)
        query = self._filter_tenant_uuid(query)
        rows, total = self.resource_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _find_query(self, criteria):
        query = self.session.query(Tenant)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Tenant.uuid.in_(self.tenant_uuids))
