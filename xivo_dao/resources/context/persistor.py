# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextmember import ContextMember

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class ContextPersistor(CriteriaBuilderMixin):

    _search_table = Context

    def __init__(self, session, context_search, tenant_uuids=None):
        self.session = session
        self.context_search = context_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Context)
        if self.tenant_uuids is not None:
            query = query.filter(Context.tenant_uuid.in_(self.tenant_uuids))
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        context = self.find_by(criteria)
        if not context:
            raise errors.not_found('Context', **criteria)
        return context

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(Context)
        if self.tenant_uuids is not None:
            query = query.filter(Context.tenant_uuid.in_(self.tenant_uuids))

        rows, total = self.context_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, context):
        self.session.add(context)
        self.session.flush()
        return context

    def edit(self, context):
        self.session.add(context)
        self.session.flush()

    def delete(self, context):
        self._delete_associations(context)
        self.session.delete(context)
        self.session.flush()

    def _delete_associations(self, context):
        (self.session.query(ContextMember)
         .filter(ContextMember.context == context.name)
         .delete())
