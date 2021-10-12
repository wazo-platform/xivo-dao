# -*- coding: utf-8 -*-
# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.conference import Conference

from xivo_dao.helpers.persistor import BasePersistor
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class ConferencePersistor(CriteriaBuilderMixin, BasePersistor):

    _search_table = Conference

    def __init__(self, session, conference_search, tenant_uuids=None):
        self.session = session
        self.search_system = conference_search
        self.tenant_uuids = tenant_uuids

    def _find_query(self, criteria):
        query = self.session.query(Conference)
        query = self._filter_tenant_uuid(query)
        return self.build_criteria(query, criteria)

    def _search_query(self):
        return self.session.query(self.search_system.config.table)

    def delete(self, conference):
        self._delete_associations(conference)
        self.session.delete(conference)
        self.session.flush()

    def _delete_associations(self, conference):
        for extension in conference.extensions:
            extension.type = 'user'
            extension.typeval = '0'
