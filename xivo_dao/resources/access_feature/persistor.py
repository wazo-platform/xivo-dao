# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin, SearchResult


class AccessFeaturesPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = AccessFeatures

    def __init__(self, session, access_feature_search):
        self.session = session
        self.access_feature_search = access_feature_search

    def _find_query(self, criteria):
        query = self.session.query(AccessFeatures)
        return self.build_criteria(query, criteria)

    def search(self, parameters):
        query = self.session.query(self.access_feature_search.config.table)
        rows, total = self.access_feature_search.search_from_query(query, parameters)
        return SearchResult(total, rows)
