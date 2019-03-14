# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from xivo_dao.alchemy.entity import Entity

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class EntityPersistor(CriteriaBuilderMixin):

    _search_table = Entity

    def __init__(self, session, entity_search, tenant_uuids=None):
        self.session = session
        self.entity_search = entity_search
        self.tenant_uuids = tenant_uuids

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Entity)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        entity = self.find_by(criteria)
        if not entity:
            raise errors.not_found('Entity', **criteria)
        return entity

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.entity_search.config.table)
        query = self._filter_tenant_uuid(query)
        rows, total = self.entity_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, entity):
        self.session.add(entity)
        self.session.flush()
        return entity

    def edit(self, entity):
        self.session.add(entity)
        self.session.flush()

    def delete(self, entity):
        self.session.delete(entity)
        self.session.flush()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(Entity.tenant_uuid.in_(self.tenant_uuids))
