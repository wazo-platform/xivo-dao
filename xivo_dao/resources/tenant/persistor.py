# Copyright 2020-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Tenant

    def __init__(self, session, search, tenant_uuids=None):
        self.session = session
        self.search_system = search
        self.tenant_uuids = tenant_uuids

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

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
