# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import text

from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CallPermissionPersistor(CriteriaBuilderMixin):

    _search_table = CallPermission

    def __init__(self, session, call_permission_search, tenant_uuids=None):
        self.session = session
        self.call_permission_search = call_permission_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(CallPermission)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        call_permission = self.find_by(criteria)
        if not call_permission:
            raise errors.not_found('CallPermission', **criteria)
        return call_permission

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.call_permission_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(CallPermission.tenant_uuid.in_(self.tenant_uuids))

    def create(self, call_permission):
        self.session.add(call_permission)
        self.session.flush()
        return call_permission

    def edit(self, call_permission):
        self.session.add(call_permission)
        self.session.flush()

    def delete(self, call_permission):
        self.session.delete(call_permission)
        self.session.flush()
