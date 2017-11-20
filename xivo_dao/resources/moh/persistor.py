# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.moh import MOH

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class MOHPersistor(CriteriaBuilderMixin):

    _search_table = MOH

    def __init__(self, session, moh_search):
        self.session = session
        self.moh_search = moh_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(MOH)
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
        rows, total = self.moh_search.search(self.session, parameters)
        return SearchResult(total, rows)

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
