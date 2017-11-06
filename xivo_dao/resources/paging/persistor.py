# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.paging import Paging

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class PagingPersistor(CriteriaBuilderMixin):

    _search_table = Paging

    def __init__(self, session, paging_search):
        self.session = session
        self.paging_search = paging_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Paging)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        paging = self.find_by(criteria)
        if not paging:
            raise errors.not_found('Paging', **criteria)
        return paging

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.paging_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, paging):
        self.session.add(paging)
        self.session.flush()
        return paging

    def edit(self, paging):
        self.session.add(paging)
        self.session.flush()

    def delete(self, paging):
        self.session.delete(paging)
        self.session.flush()
