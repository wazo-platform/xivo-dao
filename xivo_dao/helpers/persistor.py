# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult


class BasePersistor:
    def create(self, model):
        self.session.add(model)
        self.session.flush()
        return model

    def delete(self, model):
        self.session.delete(model)
        self.session.flush()

    def edit(self, model):
        self.persist(model)

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def get_by(self, criteria):
        model = self.find_by(criteria)
        if not model:
            resource_name = self._search_table.__mapper__.class_.__name__
            raise errors.not_found(resource_name, **criteria)
        return model

    def persist(self, model):
        self.session.add(model)
        self.session.flush()
        self.session.expire(model)

    def search(self, parameters):
        query = self._search_query()
        query = self._filter_tenant_uuid(query)
        rows, total = self.search_system.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def _find_query(self, criteria):
        raise NotImplementedError()

    def _filter_tenant_uuid(self, query):
        if self.tenant_uuids is None:
            return query

        if not self.tenant_uuids:
            return query.filter(text('false'))

        return query.filter(self._search_table.tenant_uuid.in_(self.tenant_uuids))
