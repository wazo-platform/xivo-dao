# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.helpers import errors
from xivo_dao.resources.line.fixes import LineFixes
from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class CustomPersistor(CriteriaBuilderMixin):

    _search_table = Custom

    def __init__(self, session, custom_search, tenant_uuids=None):
        self.session = session
        self.custom_search = custom_search
        self.tenant_uuids = tenant_uuids

    def get(self, custom_id):
        custom = self._find_query({'id': custom_id}).first()
        if not custom:
            raise errors.not_found('CustomEndpoint', id=id)
        return custom

    def _find_query(self, criteria):
        query = self.session.query(Custom)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def find_by(self, criteria):
        return self._find_query(criteria).first()

    def find_all_by(self, criteria):
        return self._find_query(criteria).all()

    def search(self, parameters):
        query = self.session.query(self.custom_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.custom_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, custom):
        self.fill_default_values(custom)
        self.session.add(custom)
        self.session.flush()
        return custom

    def fill_default_values(self, custom):
        if custom.protocol is None:
            custom.protocol = 'custom'
        if custom.category is None:
            custom.category = 'user'

    def edit(self, custom):
        self.session.add(custom)
        self.session.flush()
        self._fix_associated(custom)

    def delete(self, custom):
        self.session.query(Custom).filter_by(id=custom.id).delete()
        self.session.expire_all()
        self.session.flush()
        self._fix_associated(custom)

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Custom.tenant_uuid.in_(self.tenant_uuids))

    def _fix_associated(self, custom):
        if custom.line:
            LineFixes(self.session).fix(custom.line.id)

        if custom.trunk:
            TrunkFixes(self.session).fix(custom.trunk.id)
