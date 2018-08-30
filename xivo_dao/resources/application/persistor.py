# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text

from xivo_dao.alchemy.application import Application

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class ApplicationPersistor(CriteriaBuilderMixin):

    _search_table = Application

    def __init__(self, session, application_search, tenant_uuids=None):
        self.session = session
        self.application_search = application_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Application)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        application = self.find_by(criteria)
        if not application:
            raise errors.not_found('Application', **criteria)
        return application

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.application_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.application_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, application):
        self.session.add(application)
        self.session.flush()
        return application

    def edit(self, application):
        self.session.add(application)
        self.session.flush()

    def delete(self, application):
        self.session.delete(application)
        self.session.flush()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Application.tenant_uuid.in_(self.tenant_uuids))
