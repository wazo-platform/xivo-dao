# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.external_app import ExternalApp
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class ExternalAppPersistor(CriteriaBuilderMixin):

    _search_table = ExternalApp

    def __init__(self, session, external_app_search, tenant_uuids=None):
        self.session = session
        self.external_app_search = external_app_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(ExternalApp)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        external_app = self.find_by(criteria)
        if not external_app:
            raise errors.not_found('ExternalApp', **criteria)
        return external_app

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.external_app_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.external_app_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(ExternalApp.tenant_uuid.in_(self.tenant_uuids))

    def create(self, external_app):
        self.session.add(external_app)
        self.session.flush()
        return external_app

    def edit(self, external_app):
        self.session.add(external_app)
        self.session.flush()

    def delete(self, external_app):
        self.session.delete(external_app)
        self.session.flush()
