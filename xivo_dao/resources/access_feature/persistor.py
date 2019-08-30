# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.accessfeatures import AccessFeatures

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class AccessFeaturesPersistor(CriteriaBuilderMixin):

    _search_table = AccessFeatures

    def __init__(self, session, access_feature_search):
        self.session = session
        self.access_feature_search = access_feature_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(AccessFeatures)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        access_feature = self.find_by(criteria)
        if not access_feature:
            raise errors.not_found('AccessFeatures', **criteria)
        return access_feature

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        query = self.session.query(self.access_feature_search.config.table)
        rows, total = self.access_feature_search.search_from_query(query, parameters)
        return SearchResult(total, rows)

    def create(self, access_feature):
        self.session.add(access_feature)
        self.session.flush()
        return access_feature

    def edit(self, access_feature):
        self.session.add(access_feature)
        self.session.flush()

    def delete(self, access_feature):
        self.session.delete(access_feature)
        self.session.flush()
