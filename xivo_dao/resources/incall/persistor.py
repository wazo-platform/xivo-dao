# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class IncallPersistor(CriteriaBuilderMixin):

    _search_table = Incall

    def __init__(self, session, incall_search, tenant_uuids=None):
        self.session = session
        self.incall_search = incall_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Incall)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        incall = self.find_by(criteria)
        if not incall:
            raise errors.not_found('Incall', **criteria)
        return incall

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.incall_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.incall_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, incall):
        self.session.add(incall)
        self.session.flush()
        return incall

    def edit(self, incall):
        self.session.add(incall)
        self.session.flush()

    def delete(self, incall):
        self._delete_associations(incall)
        self.session.delete(incall)
        self.session.flush()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Incall.tenant_uuid.in_(self.tenant_uuids))

    def _delete_associations(self, incall):
        (self.session.query(Extension)
         .filter(Extension.type == 'incall')
         .filter(Extension.typeval == str(incall.id))
         .update({'type': 'user', 'typeval': '0'}))
