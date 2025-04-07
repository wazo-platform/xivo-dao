# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.feature_extension.search import feature_extension_search
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class FeatureExtensionPersistor(CriteriaBuilderMixin, BasePersistor):
    _search_table = FeatureExtension

    def __init__(self, session):
        self.session = session
        self.tenant_uuids = None
        self.search_system = feature_extension_search

    def _find_query(self, criteria):
        query = self.session.query(FeatureExtension)
        query = self.build_criteria(query, criteria)
        return query

    def _search_query(self):
        return self.session.query(FeatureExtension)

    def create(self, extension):
        self.session.add(extension)
        self.session.flush()
        return extension

    def delete(self, extension):
        self.session.query(FeatureExtension).filter(
            FeatureExtension.uuid == extension.uuid
        ).delete()
        self.session.flush()
