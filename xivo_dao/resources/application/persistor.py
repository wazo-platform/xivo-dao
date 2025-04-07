# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.application import Application
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class ApplicationPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = Application

    def __init__(self, session, application_search, tenant_uuids=None):
        self.session = session
        self.application_search = application_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Application)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def search(self, parameters):
        query = self.session.query(self.application_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.application_search.search_from_query(query, parameters)
        return SearchResult(total, rows)
