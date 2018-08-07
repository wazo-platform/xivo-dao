# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text

from xivo_dao.alchemy.moh import MOH
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class MOHPersistor(CriteriaBuilderMixin):

    _search_table = MOH

    def __init__(self, session, moh_search, tenant_uuids=None):
        self.session = session
        self.moh_search = moh_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(MOH)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        moh = self.find_by(criteria)
        if not moh:
            raise errors.not_found('MOH', **criteria)
        return moh

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.moh_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.moh_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(MOH.tenant_uuid.in_(self.tenant_uuids))

    def create(self, moh):
        self.session.add(moh)
        self.session.flush()
        return moh

    def edit(self, moh):
        self.session.add(moh)
        self.session.flush()

    def delete(self, moh):
        self.session.delete(moh)
        self.session.flush()
