# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.context import Context
from xivo_dao.alchemy.contextmember import ContextMember

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class ContextPersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Context

    def __init__(self, session, context_search, tenant_uuids=None):
        self.session = session
        self.search_system = context_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Context)
        if self.tenant_uuids is not None:
            query = query.filter(Context.tenant_uuid.in_(self.tenant_uuids))
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(Context)

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

    def associate_contexts(self, context, contexts):
        context.contexts = contexts
        self.session.flush()
