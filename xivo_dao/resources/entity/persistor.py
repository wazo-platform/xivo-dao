# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.entity import Entity

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class EntityPersistor(CriteriaBuilderMixin):

    _search_table = Entity

    def __init__(self, session, entity_search):
        self.session = session
        self.entity_search = entity_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Entity)
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
        rows, total = self.entity_search.search(self.session, parameters)
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
